from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import PaginationParams, get_current_user, get_db, get_pagination_params
from app.middleware.error_handler import APIError
from app.models import AuthorWatchlist, NotificationChannel, TopicProfile
from app.schemas.auth import UserOut
from app.schemas.common import PaginatedResponse
from app.schemas.interest import (
    AuthorWatchlistCreate,
    AuthorWatchlistOut,
    AuthorWatchlistUpdate,
    NotificationChannelOut,
    NotificationChannelUpdate,
    TopicProfileCreate,
    TopicProfileOut,
    TopicProfileUpdate,
)

router = APIRouter(prefix="/interests", tags=["Interests"])


def _paginate(items: list[TopicProfileOut] | list[AuthorWatchlistOut], total: int, params: PaginationParams) -> PaginatedResponse:
    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        per_page=params.per_page,
    )


def _serialize_profile(row) -> TopicProfileOut:
    return TopicProfileOut(
        id=row.id,
        workspace_id=row.workspace_id,
        name=row.name,
        categories=row.categories,
        keywords=row.keywords,
        is_default=row.is_default,
        created_at=row.created_at,
    )


def _serialize_watchlist(row) -> AuthorWatchlistOut:
    return AuthorWatchlistOut(
        id=row.id,
        workspace_id=row.workspace_id,
        author_name=row.author_name,
        arxiv_author_id=row.arxiv_author_id,
        notes=row.notes,
        created_at=row.created_at,
    )


def _normalize_channel_config(raw_config: object) -> dict[str, str]:
    if not isinstance(raw_config, dict):
        return {}

    normalized: dict[str, str] = {}
    for key, value in raw_config.items():
        if isinstance(value, str):
            normalized[key] = value
        elif isinstance(value, (int, float, bool)):
            normalized[key] = str(value).lower() if isinstance(value, bool) else str(value)

    target = (
        normalized.get("target")
        or normalized.get("address")
        or normalized.get("webhook_url")
        or normalized.get("endpoint")
        or normalized.get("channel")
    )
    if target:
        normalized["target"] = target

    return normalized


def _default_channel_label(channel_type: str) -> str:
    return {
        "email": "Email digest",
        "telegram": "Telegram alert",
        "discord": "Discord digest",
        "webhook": "Webhook sync",
    }.get(channel_type, channel_type.replace("_", " ").title())


def _serialize_channel(row) -> NotificationChannelOut:
    config = _normalize_channel_config(row.config)
    return NotificationChannelOut(
        id=row.id,
        workspace_id=row.workspace_id,
        channel_type=row.channel_type,
        label=config.get("label") or _default_channel_label(row.channel_type),
        config=config,
        is_active=row.is_active,
    )


async def _get_profile_row(session: AsyncSession, profile_id: UUID, workspace_id: UUID):
    row = (
        await session.execute(
            select(
                TopicProfile.id,
                TopicProfile.workspace_id,
                TopicProfile.name,
                TopicProfile.categories,
                TopicProfile.keywords,
                TopicProfile.is_default,
                TopicProfile.created_at,
            )
            .where(TopicProfile.id == profile_id)
            .where(TopicProfile.workspace_id == workspace_id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="topic_profile_not_found", message="Topic profile not found.")
    return row


async def _get_watchlist_row(session: AsyncSession, watchlist_id: UUID, workspace_id: UUID):
    row = (
        await session.execute(
            select(
                AuthorWatchlist.id,
                AuthorWatchlist.workspace_id,
                AuthorWatchlist.author_name,
                AuthorWatchlist.arxiv_author_id,
                AuthorWatchlist.notes,
                AuthorWatchlist.created_at,
            )
            .where(AuthorWatchlist.id == watchlist_id)
            .where(AuthorWatchlist.workspace_id == workspace_id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="author_watchlist_not_found", message="Author watchlist not found.")
    return row


async def _get_channel_row(session: AsyncSession, channel_id: UUID, workspace_id: UUID):
    row = (
        await session.execute(
            select(
                NotificationChannel.id,
                NotificationChannel.workspace_id,
                NotificationChannel.channel_type,
                NotificationChannel.config,
                NotificationChannel.is_active,
            )
            .where(NotificationChannel.id == channel_id)
            .where(NotificationChannel.workspace_id == workspace_id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(
            status_code=404,
            code="notification_channel_not_found",
            message="Notification channel not found.",
        )
    return row


@router.get("/topic-profiles", response_model=PaginatedResponse[TopicProfileOut])
async def list_topic_profiles(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TopicProfileOut]:
    total = (
        await session.execute(
            select(func.count())
            .select_from(TopicProfile)
            .where(TopicProfile.workspace_id == current_user.workspace_id)
        )
    ).scalar_one()

    rows = (
        await session.execute(
            select(
                TopicProfile.id,
                TopicProfile.workspace_id,
                TopicProfile.name,
                TopicProfile.categories,
                TopicProfile.keywords,
                TopicProfile.is_default,
                TopicProfile.created_at,
            )
            .where(TopicProfile.workspace_id == current_user.workspace_id)
            .order_by(TopicProfile.created_at.desc())
            .offset((pagination.page - 1) * pagination.per_page)
            .limit(pagination.per_page)
        )
    ).all()

    return _paginate([_serialize_profile(row) for row in rows], total, pagination)


@router.post("/topic-profiles", response_model=TopicProfileOut, status_code=status.HTTP_201_CREATED)
async def create_topic_profile(
    payload: TopicProfileCreate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TopicProfileOut:
    profile_id = uuid4()
    try:
        await session.execute(
            insert(TopicProfile).values(
                id=profile_id,
                workspace_id=current_user.workspace_id,
                name=payload.name,
                categories=payload.categories,
                keywords=payload.keywords,
                is_default=payload.is_default,
            )
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise APIError(status_code=409, code="topic_profile_conflict", message="Topic profile already exists.") from exc

    return _serialize_profile(await _get_profile_row(session, profile_id, current_user.workspace_id))


@router.get("/topic-profiles/{profile_id}", response_model=TopicProfileOut)
async def get_topic_profile(
    profile_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TopicProfileOut:
    return _serialize_profile(await _get_profile_row(session, profile_id, current_user.workspace_id))


@router.patch("/topic-profiles/{profile_id}", response_model=TopicProfileOut)
async def update_topic_profile(
    profile_id: UUID,
    payload: TopicProfileUpdate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TopicProfileOut:
    await _get_profile_row(session, profile_id, current_user.workspace_id)
    updates = payload.model_dump(exclude_none=True)
    if updates:
        try:
            await session.execute(
                update(TopicProfile)
                .where(TopicProfile.id == profile_id)
                .where(TopicProfile.workspace_id == current_user.workspace_id)
                .values(**updates)
            )
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise APIError(status_code=409, code="topic_profile_conflict", message="Topic profile already exists.") from exc

    return _serialize_profile(await _get_profile_row(session, profile_id, current_user.workspace_id))


@router.delete("/topic-profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic_profile(
    profile_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await _get_profile_row(session, profile_id, current_user.workspace_id)
    await session.execute(
        delete(TopicProfile)
        .where(TopicProfile.id == profile_id)
        .where(TopicProfile.workspace_id == current_user.workspace_id)
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/author-watchlists", response_model=PaginatedResponse[AuthorWatchlistOut])
async def list_author_watchlists(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AuthorWatchlistOut]:
    total = (
        await session.execute(
            select(func.count())
            .select_from(AuthorWatchlist)
            .where(AuthorWatchlist.workspace_id == current_user.workspace_id)
        )
    ).scalar_one()

    rows = (
        await session.execute(
            select(
                AuthorWatchlist.id,
                AuthorWatchlist.workspace_id,
                AuthorWatchlist.author_name,
                AuthorWatchlist.arxiv_author_id,
                AuthorWatchlist.notes,
                AuthorWatchlist.created_at,
            )
            .where(AuthorWatchlist.workspace_id == current_user.workspace_id)
            .order_by(AuthorWatchlist.created_at.desc())
            .offset((pagination.page - 1) * pagination.per_page)
            .limit(pagination.per_page)
        )
    ).all()

    return _paginate([_serialize_watchlist(row) for row in rows], total, pagination)


@router.post("/author-watchlists", response_model=AuthorWatchlistOut, status_code=status.HTTP_201_CREATED)
async def create_author_watchlist(
    payload: AuthorWatchlistCreate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AuthorWatchlistOut:
    watchlist_id = uuid4()
    try:
        await session.execute(
            insert(AuthorWatchlist).values(
                id=watchlist_id,
                workspace_id=current_user.workspace_id,
                author_name=payload.author_name,
                arxiv_author_id=payload.arxiv_author_id,
                notes=payload.notes,
            )
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise APIError(
            status_code=409,
            code="author_watchlist_conflict",
            message="Author watchlist already exists.",
        ) from exc

    return _serialize_watchlist(await _get_watchlist_row(session, watchlist_id, current_user.workspace_id))


@router.get("/author-watchlists/{watchlist_id}", response_model=AuthorWatchlistOut)
async def get_author_watchlist(
    watchlist_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AuthorWatchlistOut:
    return _serialize_watchlist(await _get_watchlist_row(session, watchlist_id, current_user.workspace_id))


@router.patch("/author-watchlists/{watchlist_id}", response_model=AuthorWatchlistOut)
async def update_author_watchlist(
    watchlist_id: UUID,
    payload: AuthorWatchlistUpdate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AuthorWatchlistOut:
    await _get_watchlist_row(session, watchlist_id, current_user.workspace_id)
    updates = payload.model_dump(exclude_none=True)
    if updates:
        try:
            await session.execute(
                update(AuthorWatchlist)
                .where(AuthorWatchlist.id == watchlist_id)
                .where(AuthorWatchlist.workspace_id == current_user.workspace_id)
                .values(**updates)
            )
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise APIError(
                status_code=409,
                code="author_watchlist_conflict",
                message="Author watchlist already exists.",
            ) from exc

    return _serialize_watchlist(await _get_watchlist_row(session, watchlist_id, current_user.workspace_id))


@router.delete("/author-watchlists/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author_watchlist(
    watchlist_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await _get_watchlist_row(session, watchlist_id, current_user.workspace_id)
    await session.execute(
        delete(AuthorWatchlist)
        .where(AuthorWatchlist.id == watchlist_id)
        .where(AuthorWatchlist.workspace_id == current_user.workspace_id)
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/channels", response_model=list[NotificationChannelOut])
async def list_notification_channels(
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[NotificationChannelOut]:
    rows = (
        await session.execute(
            select(
                NotificationChannel.id,
                NotificationChannel.workspace_id,
                NotificationChannel.channel_type,
                NotificationChannel.config,
                NotificationChannel.is_active,
            )
            .where(NotificationChannel.workspace_id == current_user.workspace_id)
            .order_by(NotificationChannel.is_active.desc(), NotificationChannel.channel_type.asc())
        )
    ).all()

    return [_serialize_channel(row) for row in rows]


@router.patch("/channels/{channel_id}", response_model=NotificationChannelOut)
async def update_notification_channel(
    channel_id: UUID,
    payload: NotificationChannelUpdate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> NotificationChannelOut:
    existing = await _get_channel_row(session, channel_id, current_user.workspace_id)
    updates = payload.model_dump(exclude_none=True)

    values: dict[str, object] = {}
    if "is_active" in updates:
        values["is_active"] = updates["is_active"]

    next_config = dict(existing.config or {})
    if "config" in updates:
        next_config.update(updates["config"])
    if "label" in updates:
        next_config["label"] = updates["label"]
    if next_config != dict(existing.config or {}):
        values["config"] = next_config

    if values:
        await session.execute(
            update(NotificationChannel)
            .where(NotificationChannel.id == channel_id)
            .where(NotificationChannel.workspace_id == current_user.workspace_id)
            .values(**values)
        )
        await session.commit()

    row = await _get_channel_row(session, channel_id, current_user.workspace_id)
    return _serialize_channel(row)
