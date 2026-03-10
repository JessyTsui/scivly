from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.deps import PaginationParams, get_current_user, get_pagination_params
from app.middleware.error_handler import APIError
from app.schemas.auth import UserOut
from app.schemas.common import PaginatedResponse, WebhookCreate, WebhookDeliveryPreview, WebhookOut, WebhookUpdate

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

WEBHOOKS = {
    UUID("23232323-2323-2323-2323-232323232323"): WebhookOut(
        id=UUID("23232323-2323-2323-2323-232323232323"),
        url="https://hooks.example.com/scivly",
        events=["paper.matched", "digest.sent"],
        is_active=True,
        secret_preview="whsec_...b91f",
        created_at=datetime(2026, 2, 28, 6, 30, tzinfo=timezone.utc),
        deliveries=[
            WebhookDeliveryPreview(
                event_type="digest.sent",
                last_status="sent",
                last_attempt_at=datetime(2026, 3, 10, 1, 16, tzinfo=timezone.utc),
            )
        ],
    )
}


def _get_webhook(webhook_id: UUID) -> WebhookOut:
    webhook = WEBHOOKS.get(webhook_id)
    if webhook is None:
        raise APIError(status_code=404, code="webhook_not_found", message="Webhook not found.")
    return webhook


@router.get("", response_model=PaginatedResponse[WebhookOut])
def list_webhooks(
    pagination: PaginationParams = Depends(get_pagination_params),
    _: UserOut = Depends(get_current_user),
) -> PaginatedResponse[WebhookOut]:
    items = sorted(WEBHOOKS.values(), key=lambda webhook: webhook.created_at, reverse=True)
    start = (pagination.page - 1) * pagination.per_page
    end = start + pagination.per_page
    return PaginatedResponse[WebhookOut](
        items=items[start:end],
        total=len(items),
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("", response_model=WebhookOut, status_code=status.HTTP_201_CREATED)
def create_webhook(payload: WebhookCreate, _: UserOut = Depends(get_current_user)) -> WebhookOut:
    return WebhookOut(
        id=UUID("24242424-2424-2424-2424-242424242424"),
        url=payload.url,
        events=payload.events,
        is_active=True,
        secret_preview=f"whsec_...{(payload.secret_hint or 'demo')[:4]}",
        created_at=datetime(2026, 3, 10, 9, 20, tzinfo=timezone.utc),
        deliveries=[],
    )


@router.get("/{webhook_id}", response_model=WebhookOut)
def get_webhook(webhook_id: UUID, _: UserOut = Depends(get_current_user)) -> WebhookOut:
    return _get_webhook(webhook_id)


@router.patch("/{webhook_id}", response_model=WebhookOut)
def update_webhook(
    webhook_id: UUID,
    payload: WebhookUpdate,
    _: UserOut = Depends(get_current_user),
) -> WebhookOut:
    webhook = _get_webhook(webhook_id)
    updates = payload.model_dump(exclude_none=True)
    return webhook.model_copy(update=updates)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(webhook_id: UUID, _: UserOut = Depends(get_current_user)) -> Response:
    _get_webhook(webhook_id)
    WEBHOOKS.pop(webhook_id, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
