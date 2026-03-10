from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.deps import get_current_user
from app.schemas.auth import UserOut
from app.schemas.common import UsageBucketOut, UsageStatsOut

router = APIRouter(prefix="/usage", tags=["Usage"])


@router.get("", response_model=UsageStatsOut)
def get_usage(
    workspace_id: UUID | None = Query(default=None),
    _: UserOut = Depends(get_current_user),
) -> UsageStatsOut:
    target_workspace = workspace_id or UUID("22222222-2222-2222-2222-222222222222")
    buckets = [
        UsageBucketOut(record_type="api_call", quantity=1240, unit_cost=0.0004, total_cost=0.496),
        UsageBucketOut(record_type="llm_token", quantity=182000, unit_cost=0.000002, total_cost=0.364),
        UsageBucketOut(record_type="pdf_download", quantity=41, unit_cost=0.01, total_cost=0.41),
        UsageBucketOut(record_type="delivery", quantity=19, unit_cost=0.02, total_cost=0.38),
    ]
    return UsageStatsOut(
        workspace_id=target_workspace,
        period_start=datetime(2026, 3, 1, 0, 0, tzinfo=timezone.utc),
        period_end=datetime(2026, 3, 31, 23, 59, tzinfo=timezone.utc),
        total_cost=round(sum(bucket.total_cost for bucket in buckets), 3),
        by_type=buckets,
        overage_warning=False,
    )
