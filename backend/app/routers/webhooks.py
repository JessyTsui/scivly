from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import PaginationParams, get_current_user, get_db, get_pagination_params
from app.middleware.error_handler import APIError
from app.models import Webhook, WebhookDelivery
from app.persistence import ensure_workspace, preview_secret
from app.schemas.auth import UserOut
from app.schemas.common import (
    PaginatedResponse,
    WebhookCreate,
    WebhookCreatedOut,
    WebhookDeliveryPreview,
    WebhookOut,
    WebhookUpdate,
)
from app.webhooks import generate_webhook_secret, normalize_webhook_events

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


async def _list_deliveries(session: AsyncSession, webhook_id: UUID) -> list[WebhookDeliveryPreview]:
    rows = (
        await session.execute(
            select(
                WebhookDelivery.event_type,
                WebhookDelivery.status,
                func.coalesce(WebhookDelivery.last_attempt_at, WebhookDelivery.created_at).label("last_attempt_at"),
            )
            .where(WebhookDelivery.webhook_id == webhook_id)
            .order_by(
                func.coalesce(WebhookDelivery.last_attempt_at, WebhookDelivery.created_at).desc(),
                WebhookDelivery.created_at.desc(),
            )
        )
    ).all()
    latest_by_event: dict[str, WebhookDeliveryPreview] = {}
    for row in rows:
        if row.event_type in latest_by_event:
            continue
        latest_by_event[row.event_type] = WebhookDeliveryPreview(
            event_type=row.event_type,
            last_status=row.status,
            last_attempt_at=row.last_attempt_at,
        )
    return list(latest_by_event.values())


async def _serialize_webhook(session: AsyncSession, row) -> WebhookOut:
    return WebhookOut(
        id=row.id,
        url=row.url,
        events=row.events or [],
        is_active=row.is_active,
        secret_preview=preview_secret(row.secret_hash),
        created_at=row.created_at,
        deliveries=await _list_deliveries(session, row.id),
    )


async def _get_webhook_row(session: AsyncSession, webhook_id: UUID, workspace_id: UUID):
    row = (
        await session.execute(
            select(
                Webhook.id,
                Webhook.url,
                Webhook.events,
                Webhook.secret_hash,
                Webhook.is_active,
                Webhook.created_at,
            )
            .where(Webhook.id == webhook_id)
            .where(Webhook.workspace_id == workspace_id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="webhook_not_found", message="Webhook not found.")
    return row


@router.get("", response_model=PaginatedResponse[WebhookOut])
async def list_webhooks(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[WebhookOut]:
    await ensure_workspace(session, current_user)
    total = (
        await session.execute(
            select(func.count())
            .select_from(Webhook)
            .where(Webhook.workspace_id == current_user.workspace_id)
        )
    ).scalar_one()

    rows = (
        await session.execute(
            select(
                Webhook.id,
                Webhook.url,
                Webhook.events,
                Webhook.secret_hash,
                Webhook.is_active,
                Webhook.created_at,
            )
            .where(Webhook.workspace_id == current_user.workspace_id)
            .order_by(Webhook.created_at.desc())
            .offset((pagination.page - 1) * pagination.per_page)
            .limit(pagination.per_page)
        )
    ).all()

    return PaginatedResponse[WebhookOut](
        items=[await _serialize_webhook(session, row) for row in rows],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("", response_model=WebhookCreatedOut, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    payload: WebhookCreate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> WebhookCreatedOut:
    await ensure_workspace(session, current_user)
    webhook_id = uuid4()
    try:
        events = normalize_webhook_events(payload.events)
    except ValueError as exc:
        raise APIError(status_code=400, code="webhook_event_invalid", message=str(exc)) from exc
    secret_hash = payload.secret or generate_webhook_secret()
    try:
        await session.execute(
            insert(Webhook).values(
                id=webhook_id,
                workspace_id=current_user.workspace_id,
                url=str(payload.url),
                events=events,
                secret_hash=secret_hash,
                is_active=True,
            )
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise APIError(status_code=409, code="webhook_conflict", message="Webhook already exists.") from exc

    row = await _get_webhook_row(session, webhook_id, current_user.workspace_id)
    serialized = await _serialize_webhook(session, row)
    return WebhookCreatedOut(**serialized.model_dump(), secret_hash=secret_hash)


@router.get("/{webhook_id}", response_model=WebhookOut)
async def get_webhook(
    webhook_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> WebhookOut:
    await ensure_workspace(session, current_user)
    row = await _get_webhook_row(session, webhook_id, current_user.workspace_id)
    return await _serialize_webhook(session, row)


@router.patch("/{webhook_id}", response_model=WebhookOut)
async def update_webhook(
    webhook_id: UUID,
    payload: WebhookUpdate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> WebhookOut:
    await ensure_workspace(session, current_user)
    await _get_webhook_row(session, webhook_id, current_user.workspace_id)
    updates = payload.model_dump(exclude_none=True)
    if "url" in updates:
        updates["url"] = str(updates["url"])
    if "events" in updates:
        try:
            updates["events"] = normalize_webhook_events(updates["events"])
        except ValueError as exc:
            raise APIError(status_code=400, code="webhook_event_invalid", message=str(exc)) from exc
    if updates:
        try:
            await session.execute(
                update(Webhook)
                .where(Webhook.id == webhook_id)
                .where(Webhook.workspace_id == current_user.workspace_id)
                .values(**updates)
            )
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise APIError(status_code=409, code="webhook_conflict", message="Webhook already exists.") from exc

    row = await _get_webhook_row(session, webhook_id, current_user.workspace_id)
    return await _serialize_webhook(session, row)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await ensure_workspace(session, current_user)
    await _get_webhook_row(session, webhook_id, current_user.workspace_id)
    await session.execute(
        delete(Webhook)
        .where(Webhook.id == webhook_id)
        .where(Webhook.workspace_id == current_user.workspace_id)
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
