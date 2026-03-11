from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import PaginationParams, get_current_user, get_db, get_pagination_params
from app.middleware.error_handler import APIError
from app.models import ApiKey
from app.schemas.auth import UserOut
from app.schemas.common import ApiKeyCreate, ApiKeyOut, ApiKeyUpdate, PaginatedResponse

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


def _serialize_api_key(row) -> ApiKeyOut:
    return ApiKeyOut(
        id=row.id,
        name=row.name,
        prefix=row.prefix,
        scopes=row.scopes or [],
        last_used_at=row.last_used_at,
        expires_at=row.expires_at,
        is_active=row.is_active,
        created_at=row.created_at,
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


@router.get("", response_model=PaginatedResponse[ApiKeyOut])
async def list_api_keys(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ApiKeyOut]:
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

    return PaginatedResponse[ApiKeyOut](
        items=[_serialize_api_key(row) for row in rows],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("", response_model=ApiKeyOut, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ApiKeyOut:
    key_id = uuid4()
    try:
        await session.execute(
            insert(ApiKey).values(
                id=key_id,
                workspace_id=current_user.workspace_id,
                name=payload.name,
                key_hash=f"sha256:{key_id.hex}",
                prefix=f"scv_{key_id.hex[:8]}",
                scopes=payload.scopes,
                expires_at=payload.expires_at,
                is_active=True,
            )
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise APIError(status_code=409, code="api_key_conflict", message="API key already exists.") from exc

    return _serialize_api_key(await _get_api_key_row(session, key_id, current_user.workspace_id))


@router.get("/{key_id}", response_model=ApiKeyOut)
async def get_api_key(
    key_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ApiKeyOut:
    return _serialize_api_key(await _get_api_key_row(session, key_id, current_user.workspace_id))


@router.patch("/{key_id}", response_model=ApiKeyOut)
async def update_api_key(
    key_id: UUID,
    payload: ApiKeyUpdate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ApiKeyOut:
    await _get_api_key_row(session, key_id, current_user.workspace_id)
    updates = payload.model_dump(exclude_none=True)
    if updates:
        await session.execute(
            update(ApiKey)
            .where(ApiKey.id == key_id)
            .where(ApiKey.workspace_id == current_user.workspace_id)
            .values(**updates)
        )
        await session.commit()

    return _serialize_api_key(await _get_api_key_row(session, key_id, current_user.workspace_id))


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await _get_api_key_row(session, key_id, current_user.workspace_id)
    await session.execute(
        delete(ApiKey)
        .where(ApiKey.id == key_id)
        .where(ApiKey.workspace_id == current_user.workspace_id)
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
