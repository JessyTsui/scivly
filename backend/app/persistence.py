from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.error_handler import APIError
from app.models import NotificationChannel, User, Workspace, WorkspaceMember
from app.schemas.auth import UserOut


async def ensure_user(session: AsyncSession, current_user: UserOut) -> None:
    stmt = insert(User).values(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        auth_provider="header",
        auth_provider_id=str(current_user.id),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[User.id],
        set_={
            "email": current_user.email,
            "name": current_user.name,
            "avatar_url": current_user.avatar_url,
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)


async def ensure_workspace(session: AsyncSession, current_user: UserOut) -> None:
    """Auto-provision user and default workspace if they do not exist yet."""
    await ensure_user(session, current_user)

    exists = (
        await session.execute(
            select(func.count())
            .select_from(WorkspaceMember)
            .where(WorkspaceMember.user_id == current_user.id)
            .where(WorkspaceMember.workspace_id == current_user.workspace_id)
        )
    ).scalar_one()

    if exists:
        return

    # Create the default workspace and membership in one transaction.
    ws_stmt = insert(Workspace).values(
        id=current_user.workspace_id,
        name=f"{current_user.name} Workspace",
        slug=f"ws-{str(current_user.workspace_id)[:8]}",
        plan="free",
        owner_id=current_user.id,
    )
    ws_stmt = ws_stmt.on_conflict_do_nothing(index_elements=[Workspace.id])
    await session.execute(ws_stmt)

    mem_stmt = insert(WorkspaceMember).values(
        workspace_id=current_user.workspace_id,
        user_id=current_user.id,
        role="owner",
    )
    mem_stmt = mem_stmt.on_conflict_do_nothing()
    await session.execute(mem_stmt)
    await session.commit()


async def resolve_notification_channels(
    session: AsyncSession,
    workspace_id: UUID,
    channel_types: list[str],
) -> list[tuple[UUID, str]]:
    if not channel_types:
        return []

    rows = (
        await session.execute(
            select(NotificationChannel.id, NotificationChannel.channel_type)
            .where(NotificationChannel.workspace_id == workspace_id)
            .where(NotificationChannel.is_active.is_(True))
            .where(NotificationChannel.channel_type.in_(channel_types))
            .order_by(NotificationChannel.channel_type.asc(), NotificationChannel.id.asc())
        )
    ).all()

    found = {row.channel_type for row in rows}
    missing = [channel_type for channel_type in channel_types if channel_type not in found]
    if missing:
        raise APIError(
            status_code=400,
            code="notification_channel_not_found",
            message=f"No active notification channel found for: {', '.join(missing)}.",
        )

    return [(row.id, row.channel_type) for row in rows]


def build_digest_title(content: dict[str, Any]) -> str:
    headline = content.get("headline")
    if isinstance(headline, str) and headline.strip():
        return headline.strip()
    return "Scivly Digest"


def build_digest_summary_markdown(content: dict[str, Any]) -> str:
    sections = content.get("sections")
    if not isinstance(sections, list) or not sections:
        return "## Summary\n- No digest sections are available yet."

    lines = ["## Highlights"]
    for section in sections:
        title = section.get("title") if isinstance(section, dict) else None
        paper_ids = section.get("paper_ids") if isinstance(section, dict) else None
        count = len(paper_ids) if isinstance(paper_ids, list) else 0
        label = title.strip() if isinstance(title, str) and title.strip() else "Untitled section"
        lines.append(f"- {label}: {count} paper(s)")
    return "\n".join(lines)


def format_rule_payload(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        parts: list[str] = []
        if value.get("type"):
            parts.append(str(value["type"]))
        if value.get("value"):
            parts.append(str(value["value"]))
        if value.get("weight") is not None:
            parts.append(f"weight={value['weight']}")
        if parts:
            return ": ".join([parts[0], ", ".join(parts[1:])]) if len(parts) > 1 else parts[0]
    return str(value)


def format_reason_payload(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("reason"), str):
        return value["reason"]
    return str(value)


def preview_secret(secret_value: str) -> str:
    suffix = secret_value[-4:] if len(secret_value) >= 4 else secret_value
    return f"whsec_...{suffix}"
