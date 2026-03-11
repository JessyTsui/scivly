from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, PrimaryKeyConstraint, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from . import Base, Vector


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("auth_provider", "auth_provider_id", name="uq_users_auth_provider_identity"),
        CheckConstraint("length(trim(email)) > 3", name="chk_users_email_nonempty"),
        Index("uq_users_email_lower", text("lower(email)"), unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    auth_provider: Mapped[str] = mapped_column(Text, nullable=False)
    auth_provider_id: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class Workspace(Base):
    __tablename__ = "workspaces"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_workspaces_slug"),
        CheckConstraint("length(trim(name)) > 0", name="chk_workspaces_name_nonempty"),
        CheckConstraint("slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'", name="chk_workspaces_slug_format"),
        CheckConstraint(
            "subscription_status IN ("
            "'free', 'trialing', 'active', 'past_due', 'canceled', "
            "'unpaid', 'incomplete', 'incomplete_expired', 'paused'"
            ")",
            name="chk_workspaces_subscription_status",
        ),
        Index("ix_workspaces_owner_id", "owner_id"),
        Index(
            "uq_workspaces_stripe_customer_id",
            "stripe_customer_id",
            unique=True,
            postgresql_where=text("stripe_customer_id IS NOT NULL"),
        ),
        Index(
            "uq_workspaces_stripe_subscription_id",
            "stripe_subscription_id",
            unique=True,
            postgresql_where=text("stripe_subscription_id IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    plan: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'free'"))
    stripe_customer_id: Mapped[str | None] = mapped_column(Text)
    stripe_subscription_id: Mapped[str | None] = mapped_column(Text)
    stripe_price_id: Mapped[str | None] = mapped_column(Text)
    subscription_status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'free'"))
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    current_period_end: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    __table_args__ = (
        PrimaryKeyConstraint("workspace_id", "user_id"),
        CheckConstraint("role IN ('owner', 'admin', 'member')", name="chk_workspace_members_role"),
        Index("ix_workspace_members_user_id", "user_id"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)
    joined_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class TopicProfile(Base):
    __tablename__ = "topic_profiles"
    __table_args__ = (
        UniqueConstraint("workspace_id", "name", name="uq_topic_profiles_workspace_name"),
        CheckConstraint("length(trim(name)) > 0", name="chk_topic_profiles_name_nonempty"),
        Index("uq_topic_profiles_default_per_workspace", "workspace_id", unique=True, postgresql_where=text("is_default")),
        Index("ix_topic_profiles_categories_gin", "categories", postgresql_using="gin"),
        Index("ix_topic_profiles_keywords_gin", "keywords", postgresql_using="gin"),
        Index(
            "ix_topic_profiles_embedding_ivfflat",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    categories: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False, server_default=text("'{}'::text[]"))
    keywords: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False, server_default=text("'{}'::text[]"))
    embedding: Mapped[Any | None] = mapped_column(Vector(1536), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class AuthorWatchlist(Base):
    __tablename__ = "author_watchlist"
    __table_args__ = (
        UniqueConstraint("workspace_id", "author_name", name="uq_author_watchlist_workspace_author_name"),
        UniqueConstraint("workspace_id", "arxiv_author_id", name="uq_author_watchlist_workspace_arxiv_author"),
        CheckConstraint("length(trim(author_name)) > 0", name="chk_author_watchlist_author_name_nonempty"),
        Index("ix_author_watchlist_workspace_id", "workspace_id"),
        Index(
            "uq_author_watchlist_workspace_author_name_lower",
            "workspace_id",
            text("lower(author_name)"),
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    author_name: Mapped[str] = mapped_column(Text, nullable=False)
    arxiv_author_id: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class NotificationChannel(Base):
    __tablename__ = "notification_channels"
    __table_args__ = (
        UniqueConstraint("id", "workspace_id", name="uq_notification_channels_id_workspace"),
        CheckConstraint(
            "channel_type IN ('email', 'telegram', 'discord', 'webhook')",
            name="chk_notification_channels_type",
        ),
        Index("ix_notification_channels_workspace_active", "workspace_id", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    channel_type: Mapped[str] = mapped_column(Text, nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
