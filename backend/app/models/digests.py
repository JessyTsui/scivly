from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class DigestSchedule(Base):
    __tablename__ = "digest_schedules"
    __table_args__ = (
        CheckConstraint("length(trim(cron_expression)) > 0", name="chk_digest_schedules_cron_nonempty"),
        CheckConstraint("length(trim(timezone)) > 0", name="chk_digest_schedules_timezone_nonempty"),
        Index("ix_digest_schedules_workspace_active", "workspace_id", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    cron_expression: Mapped[str] = mapped_column(Text, nullable=False)
    timezone: Mapped[str] = mapped_column(Text, nullable=False)
    channel_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=False, server_default=text("'{}'::uuid[]"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class Digest(Base):
    __tablename__ = "digests"
    __table_args__ = (
        UniqueConstraint("id", "workspace_id", name="uq_digests_id_workspace"),
        UniqueConstraint("workspace_id", "schedule_id", "period_start", "period_end", name="uq_digests_schedule_window"),
        CheckConstraint("status IN ('draft', 'sent', 'failed')", name="chk_digests_status"),
        CheckConstraint("period_end >= period_start", name="chk_digests_period_window"),
        Index("ix_digests_workspace_status_created_at", text("workspace_id, status, created_at DESC")),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("digest_schedules.id", ondelete="RESTRICT"),
        nullable=False,
    )
    period_start: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paper_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=False, server_default=text("'{}'::uuid[]"))
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'draft'"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class Delivery(Base):
    __tablename__ = "deliveries"
    __table_args__ = (
        UniqueConstraint("digest_id", "channel_id", name="uq_deliveries_digest_channel"),
        ForeignKeyConstraint(
            ["digest_id", "workspace_id"],
            ["digests.id", "digests.workspace_id"],
            name="fk_deliveries_digest_workspace",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["channel_id", "workspace_id"],
            ["notification_channels.id", "notification_channels.workspace_id"],
            name="fk_deliveries_channel_workspace",
            ondelete="RESTRICT",
        ),
        CheckConstraint("status IN ('queued', 'sent', 'failed')", name="chk_deliveries_status"),
        CheckConstraint("attempts >= 0", name="chk_deliveries_attempts_nonnegative"),
        CheckConstraint("status <> 'sent' OR sent_at IS NOT NULL", name="chk_deliveries_sent_at_required"),
        Index("ix_deliveries_workspace_status_created_at", text("workspace_id, status, created_at DESC")),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    digest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    channel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'queued'"))
    attempts: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    last_error: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
