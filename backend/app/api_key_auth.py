from __future__ import annotations

import datetime as dt
import hashlib
import secrets
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_paths import PUBLIC_PATHS
from app.config import Settings
from app.middleware.error_handler import APIError
from app.models import ApiKey, UsageRecord, User, Workspace
from app.schemas.auth import UserOut

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
API_KEY_PREFIX = "scv_"
API_KEY_SCOPE_RULES: tuple[tuple[str, str | None, str | None], ...] = (
    ("/workspaces", "workspace:read", None),
    ("/interests", "interests:read", "interests:write"),
    ("/papers", "papers:read", None),
    ("/digests", "digests:read", "digests:write"),
    ("/chat", "chat:read", "chat:write"),
    ("/webhooks", "webhooks:read", "webhooks:write"),
    ("/usage", "usage:read", None),
)


@dataclass(frozen=True)
class ApiKeyPrincipal:
    api_key_id: UUID
    prefix: str
    scopes: tuple[str, ...]
    workspace_id: UUID
    user: UserOut


@dataclass(frozen=True)
class RateLimitStatus:
    remaining_key: int
    remaining_workspace: int
    window_seconds: int
    limit_key: int
    limit_workspace: int


def generate_api_key_secret() -> tuple[str, str, str]:
    public_token = secrets.token_hex(5)
    private_token = secrets.token_urlsafe(24)
    token = f"{API_KEY_PREFIX}{public_token}_{private_token}"
    prefix = f"{API_KEY_PREFIX}{public_token}"
    return token, prefix, hash_api_key_secret(token)


def hash_api_key_secret(token: str) -> str:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def looks_like_api_key(token: str) -> bool:
    return token.startswith(API_KEY_PREFIX)


def normalize_scopes(scopes: list[str] | tuple[str, ...]) -> list[str]:
    return list(dict.fromkeys(scope.strip() for scope in scopes if scope.strip()))


async def authenticate_api_key(session: AsyncSession, token: str) -> ApiKeyPrincipal:
    now = dt.datetime.now(dt.UTC)
    row = (
        await session.execute(
            select(
                ApiKey.id,
                ApiKey.prefix,
                ApiKey.scopes,
                ApiKey.workspace_id,
                ApiKey.expires_at,
                ApiKey.is_active,
                Workspace.owner_id,
                User.email,
                User.name,
                User.avatar_url,
            )
            .join(Workspace, Workspace.id == ApiKey.workspace_id)
            .join(User, User.id == Workspace.owner_id)
            .where(ApiKey.key_hash == hash_api_key_secret(token))
        )
    ).one_or_none()

    if row is None:
        raise APIError(status_code=401, code="invalid_api_key", message="API key could not be verified.")
    if not row.is_active:
        raise APIError(status_code=401, code="api_key_revoked", message="API key has been revoked.")
    if row.expires_at is not None and row.expires_at <= now:
        raise APIError(status_code=401, code="api_key_expired", message="API key has expired.")

    user_name = row.name or "Workspace API"
    return ApiKeyPrincipal(
        api_key_id=row.id,
        prefix=row.prefix,
        scopes=tuple(normalize_scopes(row.scopes or [])),
        workspace_id=row.workspace_id,
        user=UserOut(
            id=row.owner_id,
            email=row.email or f"workspace-{str(row.workspace_id)[:8]}@users.scivly.invalid",
            name=user_name,
            avatar_url=row.avatar_url,
            workspace_id=row.workspace_id,
            role="owner",
        ),
    )


def scope_for_request(*, method: str, path: str) -> str | None:
    normalized_path = path.rstrip("/") or "/"

    if normalized_path in PUBLIC_PATHS or normalized_path == "/auth/me":
        return None
    if normalized_path == "/api-keys" or normalized_path.startswith("/api-keys/"):
        raise APIError(
            status_code=403,
            code="session_auth_required",
            message="API key management requires a signed-in user session.",
        )

    for prefix, read_scope, write_scope in API_KEY_SCOPE_RULES:
        if normalized_path == prefix or normalized_path.startswith(f"{prefix}/"):
            if method.upper() in SAFE_METHODS:
                return read_scope
            if write_scope is None:
                raise APIError(
                    status_code=403,
                    code="api_key_route_not_allowed",
                    message="This route is not available to API keys.",
                )
            return write_scope

    raise APIError(
        status_code=403,
        code="api_key_route_not_allowed",
        message="This route is not available to API keys.",
    )


async def enforce_api_key_policy(
    session: AsyncSession,
    *,
    principal: ApiKeyPrincipal,
    method: str,
    path: str,
    settings: Settings,
) -> RateLimitStatus:
    required_scope = scope_for_request(method=method, path=path)
    if required_scope is not None and required_scope not in principal.scopes:
        raise APIError(
            status_code=403,
            code="insufficient_scope",
            message="API key does not have permission to access this route.",
            details=[{"required_scope": required_scope}],
        )

    window_seconds = max(1, settings.api_key_rate_limit_window_seconds)
    window_start = dt.datetime.now(dt.UTC) - dt.timedelta(seconds=window_seconds)
    key_usage = await _sum_api_calls(
        session,
        workspace_id=principal.workspace_id,
        window_start=window_start,
        api_key_id=principal.api_key_id,
    )
    workspace_usage = await _sum_api_calls(
        session,
        workspace_id=principal.workspace_id,
        window_start=window_start,
    )

    if key_usage >= settings.api_key_rate_limit_per_key:
        raise APIError(
            status_code=429,
            code="api_key_rate_limited",
            message="API key rate limit exceeded.",
            details=[
                {
                    "limit": str(settings.api_key_rate_limit_per_key),
                    "window_seconds": str(window_seconds),
                    "scope": "api_key",
                }
            ],
        )
    if workspace_usage >= settings.api_key_rate_limit_per_workspace:
        raise APIError(
            status_code=429,
            code="workspace_rate_limited",
            message="Workspace API rate limit exceeded.",
            details=[
                {
                    "limit": str(settings.api_key_rate_limit_per_workspace),
                    "window_seconds": str(window_seconds),
                    "scope": "workspace",
                }
            ],
        )

    return RateLimitStatus(
        remaining_key=max(settings.api_key_rate_limit_per_key - key_usage - 1, 0),
        remaining_workspace=max(settings.api_key_rate_limit_per_workspace - workspace_usage - 1, 0),
        window_seconds=window_seconds,
        limit_key=settings.api_key_rate_limit_per_key,
        limit_workspace=settings.api_key_rate_limit_per_workspace,
    )


async def record_api_key_usage(
    session: AsyncSession,
    *,
    principal: ApiKeyPrincipal,
    method: str,
    path: str,
    status_code: int,
) -> None:
    await session.execute(
        insert(UsageRecord).values(
            workspace_id=principal.workspace_id,
            record_type="api_call",
            quantity=1,
            unit_cost=0,
            metadata_={
                "api_key_id": str(principal.api_key_id),
                "api_key_prefix": principal.prefix,
                "auth_type": "api_key",
                "method": method.upper(),
                "path": path,
                "status_code": status_code,
            },
        )
    )
    await session.execute(
        update(ApiKey)
        .where(ApiKey.id == principal.api_key_id)
        .values(last_used_at=func.now())
    )
    await session.commit()


async def _sum_api_calls(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    window_start: dt.datetime,
    api_key_id: UUID | None = None,
) -> int:
    statement = (
        select(func.coalesce(func.sum(UsageRecord.quantity), 0))
        .where(UsageRecord.workspace_id == workspace_id)
        .where(UsageRecord.record_type == "api_call")
        .where(UsageRecord.recorded_at >= window_start)
        .where(UsageRecord.metadata_["auth_type"].astext == "api_key")
    )

    if api_key_id is not None:
        statement = statement.where(UsageRecord.metadata_["api_key_id"].astext == str(api_key_id))

    value = (await session.execute(statement)).scalar_one()
    return int(float(value or 0))
