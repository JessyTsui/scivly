from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing import get_usage_limit_states, has_soft_limit_violation
from app.config import get_settings
from app.deps import get_current_user, get_db
from app.middleware.error_handler import APIError
from app.models import UsageRecord, Workspace
from app.persistence import ensure_workspace
from app.schemas.auth import UserOut
from app.schemas.common import UsageBucketOut, UsageStatsOut

router = APIRouter(prefix="/usage", tags=["Usage"])


@router.get("", response_model=UsageStatsOut)
async def get_usage(
    workspace_id: UUID | None = Query(default=None),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UsageStatsOut:
    if workspace_id is not None and workspace_id != current_user.workspace_id:
        raise APIError(
            status_code=403,
            code="workspace_access_denied",
            message="You do not have access to that workspace.",
        )

    target_workspace = workspace_id or current_user.workspace_id
    await ensure_workspace(session, current_user)
    rows = (
        await session.execute(
            select(
                UsageRecord.record_type,
                func.sum(UsageRecord.quantity).label("quantity"),
                func.avg(UsageRecord.unit_cost).label("unit_cost"),
                func.sum(UsageRecord.quantity * UsageRecord.unit_cost).label("total_cost"),
            )
            .where(UsageRecord.workspace_id == target_workspace)
            .group_by(UsageRecord.record_type)
            .order_by(UsageRecord.record_type.asc())
        )
    ).all()

    period_row = (
        await session.execute(
            select(
                func.min(UsageRecord.recorded_at).label("period_start"),
                func.max(UsageRecord.recorded_at).label("period_end"),
            )
            .where(UsageRecord.workspace_id == target_workspace)
        )
    ).one()

    workspace_plan = (
        await session.execute(select(Workspace.plan).where(Workspace.id == target_workspace))
    ).scalar_one_or_none()
    usage_limits = await get_usage_limit_states(
        session,
        workspace_id=target_workspace,
        plan=workspace_plan,
        settings=get_settings(),
    )

    buckets = [
        UsageBucketOut(
            record_type=row.record_type,
            quantity=float(row.quantity or 0),
            unit_cost=float(row.unit_cost or 0),
            total_cost=float(row.total_cost or 0),
        )
        for row in rows
    ]

    return UsageStatsOut(
        workspace_id=target_workspace,
        period_start=period_row.period_start or datetime.now(timezone.utc),
        period_end=period_row.period_end or datetime.now(timezone.utc),
        total_cost=round(sum(bucket.total_cost for bucket in buckets), 6),
        by_type=buckets,
        overage_warning=has_soft_limit_violation(usage_limits),
    )
