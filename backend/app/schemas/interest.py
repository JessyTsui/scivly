from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import APIModel


class TopicProfileCreate(APIModel):
    name: str = Field(min_length=2, max_length=80)
    categories: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    is_default: bool = False


class TopicProfileUpdate(APIModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    categories: list[str] | None = None
    keywords: list[str] | None = None
    is_default: bool | None = None


class TopicProfileOut(APIModel):
    id: UUID
    workspace_id: UUID
    name: str
    categories: list[str]
    keywords: list[str]
    is_default: bool = False
    created_at: datetime


class AuthorWatchlistCreate(APIModel):
    author_name: str = Field(min_length=2, max_length=120)
    arxiv_author_id: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=280)


class AuthorWatchlistUpdate(APIModel):
    author_name: str | None = Field(default=None, min_length=2, max_length=120)
    arxiv_author_id: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=280)


class AuthorWatchlistOut(APIModel):
    id: UUID
    workspace_id: UUID
    author_name: str
    arxiv_author_id: str | None = None
    notes: str | None = None
    created_at: datetime


class NotificationChannelOut(APIModel):
    id: UUID
    workspace_id: UUID
    channel_type: str
    label: str
    config: dict[str, str]
    is_active: bool = True


class NotificationChannelUpdate(APIModel):
    label: str | None = Field(default=None, min_length=2, max_length=120)
    config: dict[str, str] | None = None
    is_active: bool | None = None
