from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class ApiKey(Base):
    __tablename__ = "api_keys"
    __table_args__ = (
        UniqueConstraint("key_hash", name="uq_api_keys_key_hash"),
        CheckConstraint("length(trim(name)) > 0", name="chk_api_keys_name_nonempty"),
        CheckConstraint("length(trim(prefix)) > 0", name="chk_api_keys_prefix_nonempty"),
        Index("ix_api_keys_workspace_created_at", text("workspace_id, created_at DESC")),
        Index("ix_api_keys_scopes_gin", "scopes", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    key_hash: Mapped[str] = mapped_column(Text, nullable=False)
    prefix: Mapped[str] = mapped_column(Text, nullable=False)
    scopes: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False, server_default=text("'{}'::text[]"))
    last_used_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class Webhook(Base):
    __tablename__ = "webhooks"
    __table_args__ = (
        UniqueConstraint("workspace_id", "url", name="uq_webhooks_workspace_url"),
        CheckConstraint("length(trim(url)) > 0", name="chk_webhooks_url_nonempty"),
        CheckConstraint("length(trim(signing_secret)) > 0", name="chk_webhooks_signing_secret_nonempty"),
        Index("ix_webhooks_workspace_active", "workspace_id", "is_active"),
        Index("ix_webhooks_events_gin", "events", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    events: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False, server_default=text("'{}'::text[]"))
    signing_secret: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"
    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'retrying', 'sent', 'failed')",
            name="chk_webhook_deliveries_status",
        ),
        CheckConstraint("attempts >= 0", name="chk_webhook_deliveries_attempts_nonnegative"),
        CheckConstraint("length(trim(event_type)) > 0", name="chk_webhook_deliveries_event_type_nonempty"),
        Index("ix_webhook_deliveries_webhook_created_at", text("webhook_id, created_at DESC")),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    webhook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("webhooks.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'queued'"))
    attempts: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    response_status_code: Mapped[int | None] = mapped_column()
    last_error: Mapped[str | None] = mapped_column(Text)
    last_attempt_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class UsageRecord(Base):
    __tablename__ = "usage_records"
    __table_args__ = (
        CheckConstraint(
            "record_type IN ('api_call', 'llm_token', 'pdf_download', 'delivery')",
            name="chk_usage_records_type",
        ),
        CheckConstraint("quantity > 0", name="chk_usage_records_quantity_positive"),
        CheckConstraint("unit_cost >= 0", name="chk_usage_records_unit_cost_nonnegative"),
        Index("ix_usage_records_workspace_recorded_at", text("workspace_id, recorded_at DESC")),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    record_type: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    recorded_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
