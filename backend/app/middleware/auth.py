from uuid import UUID, uuid4

from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.schemas.auth import UserOut
from app.schemas.common import ErrorResponse

DEFAULT_USER_ID = UUID("11111111-1111-1111-1111-111111111111")
DEFAULT_WORKSPACE_ID = UUID("22222222-2222-2222-2222-222222222222")
VALID_ROLES = {"owner", "admin", "member"}


def _invalid_auth_header_response(request_id: str, header_name: str, reason: str) -> JSONResponse:
    payload = ErrorResponse(
        error="invalid_auth_header",
        message=f"The `{header_name}` header is invalid.",
        details=[{"header": header_name, "reason": reason}],
        request_id=request_id,
    )
    return JSONResponse(
        status_code=400,
        content=payload.model_dump(mode="json"),
        headers={"x-request-id": request_id},
    )


def _parse_uuid_header(request_id: str, header_name: str, raw_value: str, default_value: UUID) -> tuple[UUID, JSONResponse | None]:
    if not raw_value:
        return default_value, None
    try:
        return UUID(raw_value), None
    except ValueError:
        return default_value, _invalid_auth_header_response(request_id, header_name, "Expected a valid UUID string.")


class AuthContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid4()))
        raw_user_id = request.headers.get("x-scivly-user-id", str(DEFAULT_USER_ID))
        raw_workspace_id = request.headers.get("x-scivly-workspace-id", str(DEFAULT_WORKSPACE_ID))
        email = request.headers.get("x-scivly-user-email", "researcher@scivly.dev")
        role = request.headers.get("x-scivly-user-role", "owner")
        name = request.headers.get("x-scivly-user-name", "Demo Researcher")

        request.state.request_id = request_id

        user_id, error_response = _parse_uuid_header(
            request_id,
            "x-scivly-user-id",
            raw_user_id,
            DEFAULT_USER_ID,
        )
        if error_response is not None:
            return error_response

        workspace_id, error_response = _parse_uuid_header(
            request_id,
            "x-scivly-workspace-id",
            raw_workspace_id,
            DEFAULT_WORKSPACE_ID,
        )
        if error_response is not None:
            return error_response

        if role not in VALID_ROLES:
            return _invalid_auth_header_response(
                request_id,
                "x-scivly-user-role",
                "Expected one of: owner, admin, member.",
            )

        try:
            request.state.current_user = UserOut(
                id=user_id,
                email=email,
                name=name,
                avatar_url="https://images.scivly.dev/avatar/demo-researcher.png",
                workspace_id=workspace_id,
                role=role,
            )
        except ValidationError:
            # Exceptions raised inside BaseHTTPMiddleware bypass the normal FastAPI exception handlers.
            return _invalid_auth_header_response(
                request_id,
                "x-scivly-auth-context",
                "Failed to build the request user context from headers.",
            )

        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response
