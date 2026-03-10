"""Shared task models used by the worker plane."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskType(str, Enum):
    SYNC = "sync"
    MATCH = "match"
    FETCH = "fetch"
    PARSE = "parse"
    ENRICH = "enrich"
    DELIVER = "deliver"
    INDEX = "index"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD = "dead"


class TaskResultStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPayload(BaseModel):
    """Queue payload for a single worker task."""

    model_config = ConfigDict(extra="forbid")

    task_id: UUID = Field(default_factory=uuid4)
    task_type: TaskType
    workspace_id: UUID
    paper_id: UUID | None = None
    idempotency_key: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class TaskResult(BaseModel):
    """Result emitted by a pipeline step or worker execution."""

    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    status: TaskResultStatus
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    cost: float = 0.0
    duration_ms: int = 0
