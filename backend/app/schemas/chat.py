from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import APIModel


class ChatSessionCreate(APIModel):
    workspace_id: UUID
    paper_id: UUID | None = None
    session_type: Literal["paper_qa", "digest_qa", "general"] = "general"
    title: str | None = Field(default=None, max_length=120)


class ChatSessionOut(APIModel):
    id: UUID
    workspace_id: UUID
    paper_id: UUID | None = None
    session_type: Literal["paper_qa", "digest_qa", "general"]
    title: str
    created_at: datetime


class ChatMessageCreate(APIModel):
    content: str = Field(min_length=1, max_length=4000)


class ChatMessageOut(APIModel):
    id: UUID
    session_id: UUID
    role: Literal["user", "assistant"]
    content: str
    model: str | None = None
    created_at: datetime


class ChatReplyOut(APIModel):
    session: ChatSessionOut
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut
    cited_paper_ids: list[UUID] = Field(default_factory=list)
