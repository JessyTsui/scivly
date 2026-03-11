from datetime import datetime
from typing import Any, Generic, Literal, TypeVar, cast
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from app.webhooks import SUPPORTED_WEBHOOK_EVENTS

T = TypeVar("T")
WebhookEventType = Literal["paper.matched", "paper.enriched", "digest.ready", "digest.delivered"]
WebhookDeliveryStatus = Literal["queued", "retrying", "sent", "failed"]


def default_webhook_events() -> list[WebhookEventType]:
    return cast(list[WebhookEventType], list(SUPPORTED_WEBHOOK_EVENTS))


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class HealthResponse(APIModel):
    status: Literal["ok"]
    version: str


class ReadyResponse(HealthResponse):
    checks: dict[str, str]


class ErrorResponse(APIModel):
    error: str
    message: str
    details: list[dict[str, Any]] | None = None
    request_id: str | None = None


class MessageResponse(APIModel):
    message: str


class PaginatedResponse(APIModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int


class ApiKeyCreate(APIModel):
    name: str = Field(min_length=2, max_length=64)
    scopes: list[str] = Field(default_factory=lambda: ["papers:read", "digests:read"])
    expires_at: datetime | None = None


class ApiKeyUpdate(APIModel):
    name: str | None = Field(default=None, min_length=2, max_length=64)
    scopes: list[str] | None = None
    is_active: bool | None = None


class ApiKeyOut(APIModel):
    id: UUID
    name: str
    prefix: str
    scopes: list[str]
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    is_active: bool = True
    created_at: datetime
    usage_last_24h: int = 0
    usage_total: int = 0


class ApiKeyCreatedOut(ApiKeyOut):
    token: str


class UsageBucketOut(APIModel):
    record_type: Literal["api_call", "llm_token", "pdf_download", "delivery", "paper_process", "digest_sent"]
    quantity: float
    unit_cost: float
    total_cost: float


class UsageStatsOut(APIModel):
    workspace_id: UUID
    period_start: datetime
    period_end: datetime
    total_cost: float
    currency: str = "USD"
    by_type: list[UsageBucketOut]
    overage_warning: bool = False


class WebhookDeliveryPreview(APIModel):
    event_type: WebhookEventType
    last_status: WebhookDeliveryStatus
    last_attempt_at: datetime


class WebhookCreate(APIModel):
    url: AnyHttpUrl
    events: list[WebhookEventType] = Field(default_factory=default_webhook_events)
    secret: str | None = Field(default=None, min_length=8, max_length=128)


class WebhookUpdate(APIModel):
    url: AnyHttpUrl | None = None
    events: list[WebhookEventType] | None = None
    is_active: bool | None = None


class WebhookOut(APIModel):
    id: UUID
    url: AnyHttpUrl
    events: list[WebhookEventType]
    is_active: bool = True
    secret_preview: str
    created_at: datetime
    deliveries: list[WebhookDeliveryPreview] = Field(default_factory=list)


class WebhookCreatedOut(WebhookOut):
    signing_secret: str
