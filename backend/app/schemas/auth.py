from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import APIModel


class UserOut(APIModel):
    id: UUID
    email: str
    name: str
    avatar_url: str | None = None
    workspace_id: UUID
    role: Literal["owner", "admin", "member"] = "owner"


class LoginRequest(APIModel):
    email: str
    provider: Literal["magic_link", "github", "google"] = "magic_link"


class LoginResponse(APIModel):
    message: str
    redirect_url: str
    expires_in_seconds: int = 900


class AuthCallbackRequest(APIModel):
    code: str = Field(min_length=6)
    state: str | None = None


class AuthCallbackResponse(APIModel):
    access_token: str
    refresh_token: str
    issued_at: datetime
    user: UserOut
