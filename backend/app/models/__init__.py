from __future__ import annotations

from typing import Any

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import UserDefinedType


class Base(DeclarativeBase):
    """Base declarative model for Scivly ORM stubs."""


class Vector(UserDefinedType):
    cache_ok = True

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def get_col_spec(self, **kw: Any) -> str:
        return f"vector({self.dimensions})"


from .auth import AuthorWatchlist, NotificationChannel, TopicProfile, User, Workspace, WorkspaceMember
from .billing import ApiKey, UsageRecord, Webhook, WebhookDelivery
from .chat import ChatMessage, ChatSession
from .digests import Delivery, Digest, DigestSchedule
from .papers import Paper, PaperEnrichment, PaperScore
from .pipeline import PipelineTask

__all__ = [
    "ApiKey",
    "AuthorWatchlist",
    "Base",
    "ChatMessage",
    "ChatSession",
    "Delivery",
    "Digest",
    "DigestSchedule",
    "NotificationChannel",
    "Paper",
    "PaperEnrichment",
    "PaperScore",
    "PipelineTask",
    "TopicProfile",
    "UsageRecord",
    "User",
    "Vector",
    "Webhook",
    "WebhookDelivery",
    "Workspace",
    "WorkspaceMember",
]
