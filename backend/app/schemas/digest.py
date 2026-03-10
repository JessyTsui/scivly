from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import APIModel


class DigestOut(APIModel):
    id: UUID
    workspace_id: UUID
    title: str
    period_start: datetime
    period_end: datetime
    paper_ids: list[UUID]
    status: Literal["draft", "sent", "failed"]
    channel_types: list[str]
    summary_markdown: str
    created_at: datetime


class DigestPreviewRequest(APIModel):
    workspace_id: UUID
    period_start: datetime
    period_end: datetime
    limit: int = Field(default=5, ge=1, le=20)


class DigestScheduleCreate(APIModel):
    workspace_id: UUID
    cron_expression: str = Field(min_length=5, max_length=100)
    timezone: str = Field(default="UTC", min_length=2, max_length=64)
    channel_types: list[str] = Field(default_factory=lambda: ["email"])
    is_active: bool = True


class DigestScheduleUpdate(APIModel):
    cron_expression: str | None = Field(default=None, min_length=5, max_length=100)
    timezone: str | None = Field(default=None, min_length=2, max_length=64)
    channel_types: list[str] | None = None
    is_active: bool | None = None


class DigestScheduleOut(APIModel):
    id: UUID
    workspace_id: UUID
    cron_expression: str
    timezone: str
    channel_types: list[str]
    is_active: bool = True
    created_at: datetime
