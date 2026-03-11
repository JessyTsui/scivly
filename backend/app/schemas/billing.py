from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import APIModel

WorkspaceBillingPlan = Literal["free", "pro", "team", "enterprise"]
BillingUsageMetric = Literal["papers_processed", "llm_tokens", "digests_sent"]
BillingWindow = Literal["day", "month"]


class BillingUsageLimitOut(APIModel):
    key: BillingUsageMetric
    label: str
    window: BillingWindow
    used: int
    limit: int | None = None
    remaining: int | None = None
    soft_limited: bool = False


class BillingSubscriptionOut(APIModel):
    workspace_id: UUID
    plan: WorkspaceBillingPlan
    subscription_status: str
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    stripe_price_id: str | None = None
    cancel_at_period_end: bool = False
    current_period_end: datetime | None = None
    portal_available: bool = False
    usage_limits: list[BillingUsageLimitOut] = Field(default_factory=list)
    overage_warning: bool = False


class BillingCheckoutSessionCreate(APIModel):
    plan: Literal["pro"] = "pro"
    success_url: str | None = None
    cancel_url: str | None = None


class BillingPortalSessionCreate(APIModel):
    return_url: str | None = None


class BillingSessionOut(APIModel):
    id: str
    url: str
