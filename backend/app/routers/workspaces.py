from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.deps import PaginationParams, get_current_user, get_pagination_params
from app.middleware.error_handler import APIError
from app.schemas.auth import UserOut
from app.schemas.common import PaginatedResponse
from app.schemas.workspace import WorkspaceCreate, WorkspaceOut, WorkspaceUpdate

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

WORKSPACES = {
    UUID("22222222-2222-2222-2222-222222222222"): WorkspaceOut(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        name="Scivly Lab",
        slug="scivly-lab",
        plan="team",
        role="owner",
        created_at=datetime(2026, 2, 18, 9, 0, tzinfo=timezone.utc),
    ),
    UUID("33333333-3333-3333-3333-333333333333"): WorkspaceOut(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        name="Vision Watch",
        slug="vision-watch",
        plan="pro",
        role="admin",
        created_at=datetime(2026, 2, 25, 14, 30, tzinfo=timezone.utc),
    ),
}


def _paginate(items: list[WorkspaceOut], params: PaginationParams) -> PaginatedResponse[WorkspaceOut]:
    start = (params.page - 1) * params.per_page
    end = start + params.per_page
    return PaginatedResponse[WorkspaceOut](
        items=items[start:end],
        total=len(items),
        page=params.page,
        per_page=params.per_page,
    )


def _get_workspace(workspace_id: UUID) -> WorkspaceOut:
    workspace = WORKSPACES.get(workspace_id)
    if workspace is None:
        raise APIError(status_code=404, code="workspace_not_found", message="Workspace not found.")
    return workspace


@router.get("", response_model=PaginatedResponse[WorkspaceOut])
def list_workspaces(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_current_user),
) -> PaginatedResponse[WorkspaceOut]:
    items = sorted(WORKSPACES.values(), key=lambda workspace: workspace.created_at, reverse=True)
    if current_user.workspace_id in WORKSPACES:
        items = sorted(
            items,
            key=lambda workspace: workspace.id != current_user.workspace_id,
        )
    return _paginate(items, pagination)


@router.post("", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
def create_workspace(payload: WorkspaceCreate, _: UserOut = Depends(get_current_user)) -> WorkspaceOut:
    return WorkspaceOut(
        id=UUID("44444444-4444-4444-4444-444444444444"),
        name=payload.name,
        slug=payload.slug,
        plan=payload.plan,
        role="owner",
        created_at=datetime(2026, 3, 10, 10, 0, tzinfo=timezone.utc),
    )


@router.get("/{workspace_id}", response_model=WorkspaceOut)
def get_workspace(workspace_id: UUID, _: UserOut = Depends(get_current_user)) -> WorkspaceOut:
    return _get_workspace(workspace_id)


@router.patch("/{workspace_id}", response_model=WorkspaceOut)
def update_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    _: UserOut = Depends(get_current_user),
) -> WorkspaceOut:
    workspace = _get_workspace(workspace_id)
    updates = payload.model_dump(exclude_none=True)
    return workspace.model_copy(update=updates)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(workspace_id: UUID, _: UserOut = Depends(get_current_user)) -> Response:
    _get_workspace(workspace_id)
    WORKSPACES.pop(workspace_id, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
