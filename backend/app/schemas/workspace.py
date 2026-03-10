from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import APIModel


class WorkspaceCreate(APIModel):
    name: str = Field(min_length=2, max_length=80)
    slug: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9-]+$")
    plan: Literal["free", "pro", "team", "enterprise"] = "free"


class WorkspaceUpdate(APIModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    slug: str | None = Field(default=None, min_length=2, max_length=80, pattern=r"^[a-z0-9-]+$")
    plan: Literal["free", "pro", "team", "enterprise"] | None = None


class WorkspaceOut(APIModel):
    id: UUID
    name: str
    slug: str
    plan: Literal["free", "pro", "team", "enterprise"]
    role: Literal["owner", "admin", "member"]
    created_at: datetime
