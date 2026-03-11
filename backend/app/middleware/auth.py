from typing import cast
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from app.api_key_auth import (
    ApiKeyPrincipal,
    RateLimitStatus,
    authenticate_api_key,
    enforce_api_key_policy,
    looks_like_api_key,
    record_api_key_usage,
)
from app.auth_paths import PUBLIC_PATHS
from app.auth_context import build_current_user_from_token
from app.config import get_settings
from app.db import get_session_factory
from app.middleware.error_handler import APIError
from app.schemas.common import ErrorResponse


def _error_response(
    request_id: str,
    *,
    status_code: int,
    error: str,
    message: str,
    details: list[dict[str, str]] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error=error,
        message=message,
        details=details,
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json"),
        headers={"x-request-id": request_id},
    )


def _invalid_auth_header_response(request_id: str, reason: str) -> JSONResponse:
    return _error_response(
        request_id,
        status_code=400,
        error="invalid_auth_header",
        message="The `Authorization` header is invalid.",
        details=[{"header": "Authorization", "reason": reason}],
    )


def _api_error_response(request_id: str, error: APIError) -> JSONResponse:
    return _error_response(
        request_id,
        status_code=error.status_code,
        error=error.code,
        message=error.message,
        details=error.details,
    )


class AuthContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid4()))
        request.state.request_id = request_id
        authorization = request.headers.get("authorization")
        request.state.auth_type = None
        request.state.api_key = None
        request.state.rate_limit = None

        if authorization:
            parts = authorization.split(" ", 1)
            if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
                return _invalid_auth_header_response(request_id, "Expected a Bearer token.")

            try:
                token = parts[1].strip()
                settings = get_settings()
                if looks_like_api_key(token):
                    session_factory = get_session_factory()
                    async with session_factory() as session:
                        principal = await authenticate_api_key(session, token)
                        rate_limit = await enforce_api_key_policy(
                            session,
                            principal=principal,
                            method=request.method,
                            path=request.url.path,
                            settings=settings,
                        )
                    request.state.current_user = principal.user
                    request.state.auth_type = "api_key"
                    request.state.api_key = principal
                    request.state.rate_limit = rate_limit
                else:
                    request.state.current_user = build_current_user_from_token(
                        token=token,
                        settings=settings,
                    )
                    request.state.auth_type = "session"
            except APIError as error:
                return _api_error_response(request_id, error)
        elif request.url.path not in PUBLIC_PATHS:
            request.state.current_user = None

        response = await call_next(request)
        response_rate_limit = cast(RateLimitStatus | None, getattr(request.state, "rate_limit", None))
        if response_rate_limit is not None:
            response.headers["x-ratelimit-limit"] = str(response_rate_limit.limit_key)
            response.headers["x-ratelimit-remaining"] = str(response_rate_limit.remaining_key)
            response.headers["x-ratelimit-workspace-limit"] = str(response_rate_limit.limit_workspace)
            response.headers["x-ratelimit-workspace-remaining"] = str(response_rate_limit.remaining_workspace)
            response.headers["x-ratelimit-window-seconds"] = str(response_rate_limit.window_seconds)

        response_principal = cast(ApiKeyPrincipal | None, getattr(request.state, "api_key", None))
        if response_principal is not None:
            session_factory = get_session_factory()
            async with session_factory() as session:
                await record_api_key_usage(
                    session,
                    principal=response_principal,
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                )
        response.headers["x-request-id"] = request_id
        return response
