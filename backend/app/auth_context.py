from __future__ import annotations

import re
from functools import lru_cache
from typing import Any
from uuid import UUID, uuid4, uuid5

import jwt
from jwt import InvalidTokenError, PyJWKClient, PyJWKClientError

from typing import Literal, cast

from app.config import Settings
from app.middleware.error_handler import APIError
from app.schemas.auth import UserOut

AUTH_NAMESPACE = UUID("9dd27db0-6287-4602-b6ad-d9d4a70a46fa")
VALID_ROLES = {"owner", "admin", "member"}


def require_workspace_access(requested_workspace_id: UUID, current_user: UserOut) -> None:
    if requested_workspace_id != current_user.workspace_id:
        raise APIError(status_code=404, code="workspace_not_found", message="Workspace not found.")


def build_current_user_from_token(token: str, settings: Settings) -> UserOut:
    claims = verify_session_token(token=token, settings=settings)
    return build_current_user_from_claims(claims)


def verify_session_token(token: str, settings: Settings) -> dict[str, Any]:
    if settings.auth_jwt_secret:
        claims = _decode_token(
            token=token,
            key=settings.auth_jwt_secret,
            algorithms=["HS256"],
            settings=settings,
        )
    elif settings.auth_jwt_key:
        claims = _decode_token(
            token=token,
            key=settings.auth_jwt_key,
            algorithms=["RS256"],
            settings=settings,
        )
    elif settings.auth_jwks_url:
        try:
            signing_key = _get_jwk_client(settings.auth_jwks_url).get_signing_key_from_jwt(token).key
        except PyJWKClientError as exc:
            raise APIError(
                status_code=401,
                code="invalid_token",
                message="Authentication token could not be verified.",
                details=[{"reason": str(exc)}],
            ) from exc

        claims = _decode_token(
            token=token,
            key=signing_key,
            algorithms=["RS256"],
            settings=settings,
        )
    else:
        raise APIError(
            status_code=500,
            code="auth_config_missing",
            message="Authentication is not configured.",
            details=[
                {
                    "reason": "Set SCIVLY_AUTH_JWT_SECRET for local tests or CLERK_JWT_KEY/SCIVLY_AUTH_JWKS_URL for Clerk.",
                }
            ],
        )

    authorized_party = claims.get("azp")
    if settings.auth_authorized_parties:
        if not authorized_party:
            raise APIError(
                status_code=401,
                code="invalid_token",
                message="Authentication token is missing the authorized party claim.",
            )
        if str(authorized_party) not in settings.auth_authorized_parties:
            raise APIError(
                status_code=401,
                code="invalid_token",
                message="Authentication token was issued for an unexpected origin.",
                details=[{"azp": str(authorized_party)}],
            )

    if claims.get("sts") == "pending":
        raise APIError(
            status_code=401,
            code="invalid_token",
            message="Authentication token is not yet active.",
        )

    return claims


def build_current_user_from_claims(claims: dict[str, Any]) -> UserOut:
    subject = str(claims["sub"])
    workspace_id = _resolve_workspace_id(claims=claims, subject=subject)
    workspace_name = _string_value(claims.get("workspace_name")) or f"{_display_name(claims, subject)} Workspace"
    workspace_slug = _string_value(claims.get("workspace_slug")) or _slugify(workspace_name, fallback=subject[-8:].lower())
    role = _resolve_role(claims)

    return UserOut(
        id=_resolve_user_id(claims=claims, subject=subject),
        email=_string_value(claims.get("email"))
        or _string_value(claims.get("email_address"))
        or f"{subject}@users.scivly.invalid",
        name=_display_name(claims, subject),
        avatar_url=_string_value(claims.get("picture")) or _string_value(claims.get("image_url")),
        workspace_id=workspace_id,
        role=cast(Literal["owner", "admin", "member"], role),
    )


def _decode_token(
    *,
    token: str,
    key: str | bytes,
    algorithms: list[str],
    settings: Settings,
) -> dict[str, Any]:
    options = {
        "require": ["sub"],
        "verify_aud": bool(settings.auth_audience),
        "verify_iss": bool(settings.auth_issuer),
    }
    decode_kwargs: dict[str, Any] = {
        "key": key,
        "algorithms": algorithms,
        "options": options,
    }
    if settings.auth_audience:
        decode_kwargs["audience"] = settings.auth_audience
    if settings.auth_issuer:
        decode_kwargs["issuer"] = settings.auth_issuer

    try:
        payload = jwt.decode(token, **decode_kwargs)
    except InvalidTokenError as exc:
        raise APIError(
            status_code=401,
            code="invalid_token",
            message="Authentication token could not be verified.",
            details=[{"reason": str(exc)}],
        ) from exc

    if not isinstance(payload, dict):
        raise APIError(
            status_code=401,
            code="invalid_token",
            message="Authentication token payload was malformed.",
        )

    return payload


def _display_name(claims: dict[str, Any], subject: str) -> str:
    explicit_name = _string_value(claims.get("name")) or _string_value(claims.get("full_name"))
    if explicit_name:
        return explicit_name

    first_name = _string_value(claims.get("first_name"))
    last_name = _string_value(claims.get("last_name"))
    if first_name and last_name:
        return f"{first_name} {last_name}"
    if first_name:
        return first_name

    username = _string_value(claims.get("username"))
    if username:
        return username

    return f"Researcher {subject[-6:]}"


def _resolve_user_id(claims: dict[str, Any], subject: str) -> UUID:
    local_user_id = _parse_uuid(_string_value(claims.get("local_user_id")))
    if local_user_id is not None:
        return local_user_id
    return uuid5(AUTH_NAMESPACE, f"user:{subject}")


def _resolve_workspace_id(claims: dict[str, Any], subject: str) -> UUID:
    workspace_id = _parse_uuid(_string_value(claims.get("workspace_id")))
    if workspace_id is not None:
        return workspace_id
    return uuid5(AUTH_NAMESPACE, f"workspace:{subject}")


def _resolve_role(claims: dict[str, Any]) -> str:
    role = _string_value(claims.get("role"))
    if role in VALID_ROLES:
        return role
    return "owner"


@lru_cache
def _get_jwk_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


def _string_value(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _parse_uuid(raw_value: str | None) -> UUID | None:
    if not raw_value:
        return None

    try:
        return UUID(raw_value)
    except ValueError:
        return None


def _slugify(value: str, fallback: str | None = None) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if slug:
        return slug[:80]

    if fallback:
        return fallback[:80]

    return str(uuid4())
