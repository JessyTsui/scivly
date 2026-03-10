from uuid import UUID, uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.schemas.auth import UserOut

DEFAULT_USER_ID = UUID("11111111-1111-1111-1111-111111111111")
DEFAULT_WORKSPACE_ID = UUID("22222222-2222-2222-2222-222222222222")


class AuthContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid4()))
        user_id = request.headers.get("x-scivly-user-id", str(DEFAULT_USER_ID))
        workspace_id = request.headers.get("x-scivly-workspace-id", str(DEFAULT_WORKSPACE_ID))
        email = request.headers.get("x-scivly-user-email", "researcher@scivly.dev")
        role = request.headers.get("x-scivly-user-role", "owner")
        name = request.headers.get("x-scivly-user-name", "Demo Researcher")

        request.state.request_id = request_id
        request.state.current_user = UserOut(
            id=UUID(user_id),
            email=email,
            name=name,
            avatar_url="https://images.scivly.dev/avatar/demo-researcher.png",
            workspace_id=UUID(workspace_id),
            role=role,
        )

        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response
