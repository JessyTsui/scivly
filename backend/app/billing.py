from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.models import UsageRecord

WorkspaceBillingPlan = Literal["free", "pro", "team", "enterprise"]
BillingUsageMetric = Literal["papers_processed", "llm_tokens", "digests_sent"]
BillingWindow = Literal["day", "month"]


@dataclass(frozen=True)
class UsageMetricConfig:
    key: BillingUsageMetric
    label: str
    window: BillingWindow
    record_types: tuple[str, ...]


@dataclass(frozen=True)
class UsageLimitState:
    key: BillingUsageMetric
    label: str
    window: BillingWindow
    used: int
    limit: int | None
    remaining: int | None
    soft_limited: bool


USAGE_METRICS: tuple[UsageMetricConfig, ...] = (
    UsageMetricConfig(
        key="papers_processed",
        label="Papers processed",
        window="day",
        record_types=("paper_process", "pdf_download"),
    ),
    UsageMetricConfig(
        key="llm_tokens",
        label="LLM tokens",
        window="month",
        record_types=("llm_token",),
    ),
    UsageMetricConfig(
        key="digests_sent",
        label="Digests sent",
        window="month",
        record_types=("digest_sent", "delivery"),
    ),
)


def normalize_workspace_plan(plan: str | None) -> WorkspaceBillingPlan:
    if plan == "pro":
        return "pro"
    if plan == "team":
        return "team"
    if plan == "enterprise":
        return "enterprise"
    return "free"


def plan_limits_for(plan: str | None, settings: Settings) -> dict[BillingUsageMetric, int | None]:
    normalized = normalize_workspace_plan(plan)
    if normalized == "free":
        return {
            "papers_processed": settings.billing_free_papers_per_day,
            "llm_tokens": settings.billing_free_llm_tokens_per_month,
            "digests_sent": settings.billing_free_digests_per_month,
        }
    if normalized in {"pro", "team"}:
        return {
            "papers_processed": settings.billing_pro_papers_per_day,
            "llm_tokens": settings.billing_pro_llm_tokens_per_month,
            "digests_sent": settings.billing_pro_digests_per_month,
        }
    return {
        "papers_processed": None,
        "llm_tokens": None,
        "digests_sent": None,
    }


def usage_window_start(window: BillingWindow, now: dt.datetime) -> dt.datetime:
    if window == "day":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


async def get_usage_limit_states(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    plan: str | None,
    settings: Settings,
    now: dt.datetime | None = None,
) -> list[UsageLimitState]:
    usage_now = now or dt.datetime.now(dt.UTC)
    limits = plan_limits_for(plan, settings)
    states: list[UsageLimitState] = []

    for metric in USAGE_METRICS:
        period_start = usage_window_start(metric.window, usage_now)
        used = await _sum_usage(
            session,
            workspace_id=workspace_id,
            record_types=metric.record_types,
            period_start=period_start,
        )
        limit = limits[metric.key]
        remaining = None if limit is None else max(limit - used, 0)
        states.append(
            UsageLimitState(
                key=metric.key,
                label=metric.label,
                window=metric.window,
                used=used,
                limit=limit,
                remaining=remaining,
                soft_limited=limit is not None and used >= limit,
            )
        )

    return states


def has_soft_limit_violation(states: list[UsageLimitState]) -> bool:
    return any(state.soft_limited for state in states)


async def _sum_usage(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    record_types: tuple[str, ...],
    period_start: dt.datetime,
) -> int:
    value = (
        await session.execute(
            select(func.coalesce(func.sum(UsageRecord.quantity), 0))
            .where(UsageRecord.workspace_id == workspace_id)
            .where(UsageRecord.record_type.in_(record_types))
            .where(UsageRecord.recorded_at >= period_start)
        )
    ).scalar_one()
    return int(float(value or 0))
