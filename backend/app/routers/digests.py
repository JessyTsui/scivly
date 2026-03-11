from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import PaginationParams, get_current_user, get_db, get_pagination_params
from app.middleware.error_handler import APIError
from app.models import Digest, DigestSchedule, NotificationChannel, Paper, PaperScore
from app.persistence import build_digest_summary_markdown, build_digest_title, resolve_notification_channels
from app.schemas.auth import UserOut
from app.schemas.common import PaginatedResponse
from app.schemas.digest import (
    DigestContentOut,
    DigestContentSectionOut,
    DigestOut,
    DigestPreviewRequest,
    DigestScheduleCreate,
    DigestScheduleOut,
    DigestScheduleUpdate,
)

router = APIRouter(prefix="/digests", tags=["Digests"])


async def _channel_types_for_ids(session: AsyncSession, workspace_id: UUID, channel_ids: list[UUID]) -> list[str]:
    if not channel_ids:
        return []

    rows = (
        await session.execute(
            select(NotificationChannel.channel_type)
            .where(NotificationChannel.workspace_id == workspace_id)
            .where(NotificationChannel.id.in_(channel_ids))
            .order_by(NotificationChannel.channel_type.asc())
        )
    ).all()
    return [row.channel_type for row in rows]


def _serialize_digest_content(raw_content: object) -> DigestContentOut:
    if not isinstance(raw_content, dict):
        return DigestContentOut()

    sections: list[DigestContentSectionOut] = []
    for section in raw_content.get("sections", []):
        if not isinstance(section, dict):
            continue

        paper_ids: list[UUID] = []
        for paper_id in section.get("paper_ids", []):
            try:
                paper_ids.append(UUID(str(paper_id)))
            except (TypeError, ValueError):
                continue

        title = section.get("title")
        if not isinstance(title, str) or not title.strip():
            title = "Untitled section"

        summary = section.get("summary")
        sections.append(
            DigestContentSectionOut(
                title=title.strip(),
                paper_ids=paper_ids,
                summary=summary if isinstance(summary, str) else None,
            )
        )

    headline = raw_content.get("headline")
    return DigestContentOut(
        headline=headline.strip() if isinstance(headline, str) and headline.strip() else None,
        sections=sections,
    )


def _serialize_digest(row, channel_types: list[str]) -> DigestOut:
    content = row.content or {}
    return DigestOut(
        id=row.id,
        workspace_id=row.workspace_id,
        schedule_id=row.schedule_id,
        title=build_digest_title(content),
        period_start=row.period_start,
        period_end=row.period_end,
        paper_ids=row.paper_ids or [],
        status=row.status,
        channel_types=channel_types,
        summary_markdown=build_digest_summary_markdown(content),
        content=_serialize_digest_content(content),
        created_at=row.created_at,
    )


def _serialize_schedule(row, channel_types: list[str]) -> DigestScheduleOut:
    return DigestScheduleOut(
        id=row.id,
        workspace_id=row.workspace_id,
        cron_expression=row.cron_expression,
        timezone=row.timezone,
        channel_types=channel_types,
        is_active=row.is_active,
        created_at=row.created_at,
    )


async def _get_schedule_row(session: AsyncSession, schedule_id: UUID, workspace_id: UUID):
    row = (
        await session.execute(
            select(
                DigestSchedule.id,
                DigestSchedule.workspace_id,
                DigestSchedule.cron_expression,
                DigestSchedule.timezone,
                DigestSchedule.channel_ids,
                DigestSchedule.is_active,
                DigestSchedule.created_at,
            )
            .where(DigestSchedule.id == schedule_id)
            .where(DigestSchedule.workspace_id == workspace_id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="digest_schedule_not_found", message="Digest schedule not found.")
    return row


async def _get_digest_row(session: AsyncSession, digest_id: UUID, workspace_id: UUID):
    row = (
        await session.execute(
            select(
                Digest.id,
                Digest.workspace_id,
                Digest.schedule_id,
                Digest.period_start,
                Digest.period_end,
                Digest.paper_ids,
                Digest.content,
                Digest.status,
                Digest.created_at,
            )
            .where(Digest.id == digest_id)
            .where(Digest.workspace_id == workspace_id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="digest_not_found", message="Digest not found.")
    return row


@router.get("", response_model=PaginatedResponse[DigestOut])
async def list_digests(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DigestOut]:
    total = (
        await session.execute(
            select(func.count())
            .select_from(Digest)
            .where(Digest.workspace_id == current_user.workspace_id)
        )
    ).scalar_one()

    rows = (
        await session.execute(
            select(
                Digest.id,
                Digest.workspace_id,
                Digest.schedule_id,
                Digest.period_start,
                Digest.period_end,
                Digest.paper_ids,
                Digest.content,
                Digest.status,
                Digest.created_at,
            )
            .where(Digest.workspace_id == current_user.workspace_id)
            .order_by(Digest.created_at.desc())
            .offset((pagination.page - 1) * pagination.per_page)
            .limit(pagination.per_page)
        )
    ).all()

    items: list[DigestOut] = []
    for row in rows:
        schedule_row = await _get_schedule_row(session, row.schedule_id, current_user.workspace_id)
        channel_types = await _channel_types_for_ids(session, current_user.workspace_id, schedule_row.channel_ids or [])
        items.append(_serialize_digest(row, channel_types))

    return PaginatedResponse[DigestOut](
        items=items,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.get("/schedules", response_model=PaginatedResponse[DigestScheduleOut])
async def list_schedules(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DigestScheduleOut]:
    total = (
        await session.execute(
            select(func.count())
            .select_from(DigestSchedule)
            .where(DigestSchedule.workspace_id == current_user.workspace_id)
        )
    ).scalar_one()

    rows = (
        await session.execute(
            select(
                DigestSchedule.id,
                DigestSchedule.workspace_id,
                DigestSchedule.cron_expression,
                DigestSchedule.timezone,
                DigestSchedule.channel_ids,
                DigestSchedule.is_active,
                DigestSchedule.created_at,
            )
            .where(DigestSchedule.workspace_id == current_user.workspace_id)
            .order_by(DigestSchedule.created_at.desc())
            .offset((pagination.page - 1) * pagination.per_page)
            .limit(pagination.per_page)
        )
    ).all()

    items = [
        _serialize_schedule(
            row,
            await _channel_types_for_ids(session, current_user.workspace_id, row.channel_ids or []),
        )
        for row in rows
    ]
    return PaginatedResponse[DigestScheduleOut](
        items=items,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("/schedules", response_model=DigestScheduleOut, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    payload: DigestScheduleCreate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DigestScheduleOut:
    schedule_id = uuid4()
    channels = await resolve_notification_channels(session, current_user.workspace_id, payload.channel_types)
    channel_ids = [channel_id for channel_id, _ in channels]

    await session.execute(
        insert(DigestSchedule).values(
            id=schedule_id,
            workspace_id=current_user.workspace_id,
            cron_expression=payload.cron_expression,
            timezone=payload.timezone,
            channel_ids=channel_ids,
            is_active=payload.is_active,
        )
    )
    await session.commit()

    row = await _get_schedule_row(session, schedule_id, current_user.workspace_id)
    return _serialize_schedule(row, [channel_type for _, channel_type in channels])


@router.patch("/schedules/{schedule_id}", response_model=DigestScheduleOut)
async def update_schedule(
    schedule_id: UUID,
    payload: DigestScheduleUpdate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DigestScheduleOut:
    existing = await _get_schedule_row(session, schedule_id, current_user.workspace_id)
    updates = payload.model_dump(exclude_none=True)

    channel_types = await _channel_types_for_ids(session, current_user.workspace_id, existing.channel_ids or [])
    if "channel_types" in updates:
        channels = await resolve_notification_channels(session, current_user.workspace_id, updates.pop("channel_types"))
        updates["channel_ids"] = [channel_id for channel_id, _ in channels]
        channel_types = [channel_type for _, channel_type in channels]

    if updates:
        await session.execute(
            update(DigestSchedule)
            .where(DigestSchedule.id == schedule_id)
            .where(DigestSchedule.workspace_id == current_user.workspace_id)
            .values(**updates)
        )
        await session.commit()

    row = await _get_schedule_row(session, schedule_id, current_user.workspace_id)
    return _serialize_schedule(row, channel_types)


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await _get_schedule_row(session, schedule_id, current_user.workspace_id)
    await session.execute(
        delete(DigestSchedule)
        .where(DigestSchedule.id == schedule_id)
        .where(DigestSchedule.workspace_id == current_user.workspace_id)
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/preview", response_model=DigestOut)
async def preview_digest(
    payload: DigestPreviewRequest,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DigestOut:
    rows = (
        await session.execute(
            select(Paper.id)
            .join(PaperScore, PaperScore.paper_id == Paper.id)
            .where(PaperScore.workspace_id == current_user.workspace_id)
            .where(Paper.published_at >= payload.period_start)
            .where(Paper.published_at <= payload.period_end)
            .group_by(Paper.id, Paper.published_at)
            .order_by(func.max(PaperScore.total_score).desc(), Paper.published_at.desc())
            .limit(payload.limit)
        )
    ).all()

    paper_ids = [row.id for row in rows]
    active_channels = (
        await session.execute(
            select(NotificationChannel.channel_type)
            .where(NotificationChannel.workspace_id == current_user.workspace_id)
            .where(NotificationChannel.is_active.is_(True))
            .order_by(NotificationChannel.channel_type.asc())
        )
    ).all()
    channel_types = [row.channel_type for row in active_channels] or ["email"]

    summary_markdown = "## Preview\n"
    summary_markdown += f"- Selected {len(paper_ids)} paper(s) for the requested window."

    return DigestOut(
        id=uuid4(),
        workspace_id=current_user.workspace_id,
        schedule_id=uuid4(),
        title="Preview Digest",
        period_start=payload.period_start,
        period_end=payload.period_end,
        paper_ids=paper_ids,
        status="draft",
        channel_types=channel_types,
        summary_markdown=summary_markdown,
        content=DigestContentOut(),
        created_at=payload.period_end,
    )


@router.get("/{digest_id}", response_model=DigestOut)
async def get_digest(
    digest_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DigestOut:
    row = await _get_digest_row(session, digest_id, current_user.workspace_id)
    schedule_row = await _get_schedule_row(session, row.schedule_id, current_user.workspace_id)
    channel_types = await _channel_types_for_ids(session, current_user.workspace_id, schedule_row.channel_ids or [])
    return _serialize_digest(row, channel_types)
