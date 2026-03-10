from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class PipelineTask(Base):
    __tablename__ = "pipeline_tasks"
    __table_args__ = (
        UniqueConstraint("workspace_id", "idempotency_key", name="uq_pipeline_tasks_workspace_idempotency_key"),
        CheckConstraint(
            "task_type IN ('sync', 'match', 'fetch', 'parse', 'enrich', 'deliver', 'index')",
            name="chk_pipeline_tasks_type",
        ),
        CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed', 'dead')",
            name="chk_pipeline_tasks_status",
        ),
        CheckConstraint("attempts >= 0", name="chk_pipeline_tasks_attempts_nonnegative"),
        CheckConstraint("max_attempts > 0", name="chk_pipeline_tasks_max_attempts_positive"),
        CheckConstraint("cost >= 0", name="chk_pipeline_tasks_cost_nonnegative"),
        CheckConstraint(
            "started_at IS NULL OR started_at >= created_at",
            name="chk_pipeline_tasks_started_after_created",
        ),
        CheckConstraint(
            "completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at",
            name="chk_pipeline_tasks_completed_after_started",
        ),
        Index("ix_pipeline_tasks_workspace_status_created_at", text("workspace_id, status, created_at DESC")),
        Index("ix_pipeline_tasks_paper_id", "paper_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    paper_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="SET NULL"),
    )
    task_type: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'queued'"))
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    attempts: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    max_attempts: Mapped[int] = mapped_column(nullable=False, server_default=text("5"))
    last_error: Mapped[str | None] = mapped_column(Text)
    cost: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, server_default=text("0"))
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
