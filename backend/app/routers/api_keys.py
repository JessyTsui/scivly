from __future__ import annotations

import datetime as dt
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import case, func, insert, literal_column, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_key_auth import generate_api_key_secret, normalize_scopes
from app.deps import PaginationParams, get_db, get_pagination_params, get_session_user
from app.middleware.error_handler import APIError
from app.models import ApiKey, UsageRecord
from app.persistence import ensure_workspace
from app.schemas.auth import UserOut
from app.schemas.common import ApiKeyCreate, ApiKeyCreatedOut, ApiKeyOut, ApiKeyUpdate, PaginatedResponse

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


def _serialize_api_key(row, usage: dict[str, dict[str, int]]) -> ApiKeyOut:
    usage_entry = usage.get(str(row.id), {})
    return ApiKeyOut(
        id=row.id,
        name=row.name,
        prefix=row.prefix,
        scopes=row.scopes or [],
        last_used_at=row.last_used_at,
        expires_at=row.expires_at,
        is_active=row.is_active,
        created_at=row.created_at,
        usage_last_24h=usage_entry.get("usage_last_24h", 0),
        usage_total=usage_entry.get("usage_total", 0),
    )


async def _get_api_key_row(session: AsyncSession, key_id: UUID, workspace_id: UUID):
    row = (
        await session.execute(
            select(
                ApiKey.id,
                ApiKey.name,
                ApiKey.prefix,
                ApiKey.scopes,
                ApiKey.last_used_at,
                ApiKey.expires_at,
                ApiKey.is_active,
                ApiKey.created_at,
            )
            .where(ApiKey.id == key_id)
            .where(ApiKey.workspace_id == workspace_id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="api_key_not_found", message="API key not found.")
    return row


async def _get_usage_map(session: AsyncSession, workspace_id: UUID) -> dict[str, dict[str, int]]:
    last_24h = dt.datetime.now(dt.UTC) - dt.timedelta(hours=24)
    api_key_id_expr = literal_column("usage_records.metadata ->> 'api_key_id'")
    rows = (
        await session.execute(
            select(
                api_key_id_expr.label("api_key_id"),
                func.coalesce(func.sum(UsageRecord.quantity), 0).label("usage_total"),
                func.coalesce(
                    func.sum(
                        case(
                            (UsageRecord.recorded_at >= last_24h, UsageRecord.quantity),
                            else_=0,
                        )
                    ),
                    0,
                ).label("usage_last_24h"),
            )
            .where(UsageRecord.workspace_id == workspace_id)
            .where(UsageRecord.record_type == "api_call")
            .where(UsageRecord.metadata_["auth_type"].astext == "api_key")
            .group_by(api_key_id_expr)
        )
    ).all()

    return {
        row.api_key_id: {
            "usage_total": int(float(row.usage_total or 0)),
            "usage_last_24h": int(float(row.usage_last_24h or 0)),
        }
        for row in rows
        if row.api_key_id
    }


@router.get("", response_model=PaginatedResponse[ApiKeyOut])
async def list_api_keys(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_session_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ApiKeyOut]:
    await ensure_workspace(session, current_user)
    total = (
        await session.execute(
            select(func.count())
            .select_from(ApiKey)
            .where(ApiKey.workspace_id == current_user.workspace_id)
        )
    ).scalar_one()

    rows = (
        await session.execute(
            select(
                ApiKey.id,
                ApiKey.name,
                ApiKey.prefix,
                ApiKey.scopes,
                ApiKey.last_used_at,
                ApiKey.expires_at,
                ApiKey.is_active,
                ApiKey.created_at,
            )
            .where(ApiKey.workspace_id == current_user.workspace_id)
            .order_by(ApiKey.created_at.desc())
            .offset((pagination.page - 1) * pagination.per_page)
            .limit(pagination.per_page)
        )
    ).all()
    usage = await _get_usage_map(session, current_user.workspace_id)

    return PaginatedResponse[ApiKeyOut](
        items=[_serialize_api_key(row, usage) for row in rows],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("", response_model=ApiKeyCreatedOut, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreate,
    current_user: UserOut = Depends(get_session_user),
    session: AsyncSession = Depends(get_db),
) -> ApiKeyCreatedOut:
    await ensure_workspace(session, current_user)
    key_id = uuid4()
    token, prefix, key_hash = generate_api_key_secret()
    try:
        await session.execute(
            insert(ApiKey).values(
                id=key_id,
                workspace_id=current_user.workspace_id,
                name=payload.name,
                key_hash=key_hash,
                prefix=prefix,
                scopes=normalize_scopes(payload.scopes),
                expires_at=payload.expires_at,
                is_active=True,
            )
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise APIError(status_code=409, code="api_key_conflict", message="API key already exists.") from exc

    row = await _get_api_key_row(session, key_id, current_user.workspace_id)
    data = _serialize_api_key(row, {})
    return ApiKeyCreatedOut(**data.model_dump(), token=token)


@router.get("/{key_id}", response_model=ApiKeyOut)
async def get_api_key(
    key_id: UUID,
    current_user: UserOut = Depends(get_session_user),
    session: AsyncSession = Depends(get_db),
) -> ApiKeyOut:
    await ensure_workspace(session, current_user)
    usage = await _get_usage_map(session, current_user.workspace_id)
    return _serialize_api_key(await _get_api_key_row(session, key_id, current_user.workspace_id), usage)


@router.patch("/{key_id}", response_model=ApiKeyOut)
async def update_api_key(
    key_id: UUID,
    payload: ApiKeyUpdate,
    current_user: UserOut = Depends(get_session_user),
    session: AsyncSession = Depends(get_db),
) -> ApiKeyOut:
    await ensure_workspace(session, current_user)
    await _get_api_key_row(session, key_id, current_user.workspace_id)
    updates = payload.model_dump(exclude_none=True)
    if "scopes" in updates:
        updates["scopes"] = normalize_scopes(updates["scopes"])
    if updates:
        await session.execute(
            update(ApiKey)
            .where(ApiKey.id == key_id)
            .where(ApiKey.workspace_id == current_user.workspace_id)
            .values(**updates)
        )
        await session.commit()

    usage = await _get_usage_map(session, current_user.workspace_id)
    return _serialize_api_key(await _get_api_key_row(session, key_id, current_user.workspace_id), usage)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: UUID,
    current_user: UserOut = Depends(get_session_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await ensure_workspace(session, current_user)
    await _get_api_key_row(session, key_id, current_user.workspace_id)
    await session.execute(
        update(ApiKey)
        .where(ApiKey.id == key_id)
        .where(ApiKey.workspace_id == current_user.workspace_id)
        .values(is_active=False)
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
