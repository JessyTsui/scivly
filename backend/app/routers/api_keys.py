from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.deps import PaginationParams, get_current_user, get_pagination_params
from app.middleware.error_handler import APIError
from app.schemas.auth import UserOut
from app.schemas.common import ApiKeyCreate, ApiKeyOut, ApiKeyUpdate, PaginatedResponse

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

API_KEYS = {
    UUID("25252525-2525-2525-2525-252525252525"): ApiKeyOut(
        id=UUID("25252525-2525-2525-2525-252525252525"),
        name="Frontend Preview",
        prefix="sk_live_sciv",
        scopes=["papers:read", "digests:read"],
        last_used_at=datetime(2026, 3, 9, 22, 10, tzinfo=timezone.utc),
        expires_at=None,
        is_active=True,
        created_at=datetime(2026, 2, 26, 13, 0, tzinfo=timezone.utc),
    )
}


def _get_api_key(key_id: UUID) -> ApiKeyOut:
    api_key = API_KEYS.get(key_id)
    if api_key is None:
        raise APIError(status_code=404, code="api_key_not_found", message="API key not found.")
    return api_key


@router.get("", response_model=PaginatedResponse[ApiKeyOut])
def list_api_keys(
    pagination: PaginationParams = Depends(get_pagination_params),
    _: UserOut = Depends(get_current_user),
) -> PaginatedResponse[ApiKeyOut]:
    items = sorted(API_KEYS.values(), key=lambda api_key: api_key.created_at, reverse=True)
    start = (pagination.page - 1) * pagination.per_page
    end = start + pagination.per_page
    return PaginatedResponse[ApiKeyOut](
        items=items[start:end],
        total=len(items),
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("", response_model=ApiKeyOut, status_code=status.HTTP_201_CREATED)
def create_api_key(payload: ApiKeyCreate, _: UserOut = Depends(get_current_user)) -> ApiKeyOut:
    return ApiKeyOut(
        id=UUID("26262626-2626-2626-2626-262626262626"),
        name=payload.name,
        prefix="sk_test_sciv",
        scopes=payload.scopes,
        last_used_at=None,
        expires_at=payload.expires_at,
        is_active=True,
        created_at=datetime(2026, 3, 10, 9, 10, tzinfo=timezone.utc),
    )


@router.get("/{key_id}", response_model=ApiKeyOut)
def get_api_key(key_id: UUID, _: UserOut = Depends(get_current_user)) -> ApiKeyOut:
    return _get_api_key(key_id)


@router.patch("/{key_id}", response_model=ApiKeyOut)
def update_api_key(
    key_id: UUID,
    payload: ApiKeyUpdate,
    _: UserOut = Depends(get_current_user),
) -> ApiKeyOut:
    api_key = _get_api_key(key_id)
    updates = payload.model_dump(exclude_none=True)
    return api_key.model_copy(update=updates)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(key_id: UUID, _: UserOut = Depends(get_current_user)) -> Response:
    _get_api_key(key_id)
    API_KEYS.pop(key_id, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
