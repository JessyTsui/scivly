from datetime import datetime
from typing import Any, Generic, Literal, TypeVar
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

T = TypeVar("T")


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


class UsageBucketOut(APIModel):
    record_type: Literal["api_call", "llm_token", "pdf_download", "delivery"]
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
    event_type: str
    last_status: str
    last_attempt_at: datetime


class WebhookCreate(APIModel):
    url: AnyHttpUrl
    events: list[str] = Field(default_factory=lambda: ["paper.matched", "digest.sent"])
    secret_hint: str | None = Field(default=None, max_length=16)


class WebhookUpdate(APIModel):
    url: AnyHttpUrl | None = None
    events: list[str] | None = None
    is_active: bool | None = None


class WebhookOut(APIModel):
    id: UUID
    url: AnyHttpUrl
    events: list[str]
    is_active: bool = True
    secret_preview: str
    created_at: datetime
    deliveries: list[WebhookDeliveryPreview] = Field(default_factory=list)
