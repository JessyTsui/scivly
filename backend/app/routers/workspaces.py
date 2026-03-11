from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import case, delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import PaginationParams, get_current_user, get_db, get_pagination_params
from app.middleware.error_handler import APIError
from app.models import Workspace, WorkspaceMember
from app.persistence import ensure_user
from app.schemas.auth import UserOut
from app.schemas.common import PaginatedResponse
from app.schemas.workspace import WorkspaceCreate, WorkspaceOut, WorkspaceUpdate

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


def _serialize_workspace(row) -> WorkspaceOut:
    return WorkspaceOut(
        id=row.id,
        name=row.name,
        slug=row.slug,
        plan=row.plan,
        role=row.role,
        created_at=row.created_at,
    )


async def _get_workspace_row(session: AsyncSession, workspace_id: UUID, user_id: UUID):
    row = (
        await session.execute(
            select(
                Workspace.id,
                Workspace.name,
                Workspace.slug,
                Workspace.plan,
                Workspace.created_at,
                WorkspaceMember.role,
            )
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(Workspace.id == workspace_id)
            .where(WorkspaceMember.user_id == user_id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="workspace_not_found", message="Workspace not found.")
    return row


@router.get("", response_model=PaginatedResponse[WorkspaceOut])
async def list_workspaces(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[WorkspaceOut]:
    total = (
        await session.execute(
            select(func.count())
            .select_from(WorkspaceMember)
            .where(WorkspaceMember.user_id == current_user.id)
        )
    ).scalar_one()

    rows = (
        await session.execute(
            select(
                Workspace.id,
                Workspace.name,
                Workspace.slug,
                Workspace.plan,
                Workspace.created_at,
                WorkspaceMember.role,
            )
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == current_user.id)
            .order_by(
                case((Workspace.id == current_user.workspace_id, 0), else_=1),
                Workspace.created_at.desc(),
            )
            .offset((pagination.page - 1) * pagination.per_page)
            .limit(pagination.per_page)
        )
    ).all()

    return PaginatedResponse[WorkspaceOut](
        items=[_serialize_workspace(row) for row in rows],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceOut:
    workspace_id = uuid4()

    try:
        await ensure_user(session, current_user)
        await session.execute(
            insert(Workspace).values(
                id=workspace_id,
                name=payload.name,
                slug=payload.slug,
                plan=payload.plan,
                owner_id=current_user.id,
            )
        )
        await session.execute(
            insert(WorkspaceMember).values(
                workspace_id=workspace_id,
                user_id=current_user.id,
                role="owner",
            )
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise APIError(status_code=409, code="workspace_conflict", message="Workspace slug already exists.") from exc

    row = await _get_workspace_row(session, workspace_id, current_user.id)
    return _serialize_workspace(row)


@router.get("/{workspace_id}", response_model=WorkspaceOut)
async def get_workspace(
    workspace_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceOut:
    return _serialize_workspace(await _get_workspace_row(session, workspace_id, current_user.id))


@router.patch("/{workspace_id}", response_model=WorkspaceOut)
async def update_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceOut:
    await _get_workspace_row(session, workspace_id, current_user.id)

    updates = payload.model_dump(exclude_none=True)
    if updates:
        try:
            await session.execute(update(Workspace).where(Workspace.id == workspace_id).values(**updates))
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise APIError(status_code=409, code="workspace_conflict", message="Workspace slug already exists.") from exc

    row = await _get_workspace_row(session, workspace_id, current_user.id)
    return _serialize_workspace(row)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await _get_workspace_row(session, workspace_id, current_user.id)
    await session.execute(delete(Workspace).where(Workspace.id == workspace_id))
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
