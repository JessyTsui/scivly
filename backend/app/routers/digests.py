from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.deps import PaginationParams, get_current_user, get_pagination_params
from app.middleware.error_handler import APIError
from app.schemas.auth import UserOut
from app.schemas.common import PaginatedResponse
from app.schemas.digest import (
    DigestOut,
    DigestPreviewRequest,
    DigestScheduleCreate,
    DigestScheduleOut,
    DigestScheduleUpdate,
)

router = APIRouter(prefix="/digests", tags=["Digests"])

DIGESTS = {
    UUID("12121212-1212-1212-1212-121212121212"): DigestOut(
        id=UUID("12121212-1212-1212-1212-121212121212"),
        workspace_id=UUID("22222222-2222-2222-2222-222222222222"),
        title="Daily Research Briefing",
        period_start=datetime(2026, 3, 9, 0, 0, tzinfo=timezone.utc),
        period_end=datetime(2026, 3, 9, 23, 59, tzinfo=timezone.utc),
        paper_ids=[
            UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        ],
        status="sent",
        channel_types=["email", "telegram"],
        summary_markdown="## Highlights\n- Two high-signal papers cleared the digest threshold.\n- One robotics benchmark needs deeper PDF parsing.",
        created_at=datetime(2026, 3, 10, 1, 15, tzinfo=timezone.utc),
    )
}

SCHEDULES = {
    UUID("13131313-1313-1313-1313-131313131313"): DigestScheduleOut(
        id=UUID("13131313-1313-1313-1313-131313131313"),
        workspace_id=UUID("22222222-2222-2222-2222-222222222222"),
        cron_expression="0 8 * * *",
        timezone="Asia/Shanghai",
        channel_types=["email", "telegram"],
        is_active=True,
        created_at=datetime(2026, 2, 18, 9, 5, tzinfo=timezone.utc),
    )
}


def _paginate(items: list[DigestOut] | list[DigestScheduleOut], params: PaginationParams) -> PaginatedResponse:
    start = (params.page - 1) * params.per_page
    end = start + params.per_page
    return PaginatedResponse(
        items=items[start:end],
        total=len(items),
        page=params.page,
        per_page=params.per_page,
    )


def _get_digest(digest_id: UUID) -> DigestOut:
    digest = DIGESTS.get(digest_id)
    if digest is None:
        raise APIError(status_code=404, code="digest_not_found", message="Digest not found.")
    return digest


def _get_schedule(schedule_id: UUID) -> DigestScheduleOut:
    schedule = SCHEDULES.get(schedule_id)
    if schedule is None:
        raise APIError(status_code=404, code="digest_schedule_not_found", message="Digest schedule not found.")
    return schedule


@router.get("", response_model=PaginatedResponse[DigestOut])
def list_digests(
    pagination: PaginationParams = Depends(get_pagination_params),
    _: UserOut = Depends(get_current_user),
) -> PaginatedResponse[DigestOut]:
    items = sorted(DIGESTS.values(), key=lambda digest: digest.created_at, reverse=True)
    return _paginate(items, pagination)


@router.get("/schedules", response_model=PaginatedResponse[DigestScheduleOut])
def list_schedules(
    pagination: PaginationParams = Depends(get_pagination_params),
    _: UserOut = Depends(get_current_user),
) -> PaginatedResponse[DigestScheduleOut]:
    items = sorted(SCHEDULES.values(), key=lambda schedule: schedule.created_at, reverse=True)
    return _paginate(items, pagination)


@router.post("/schedules", response_model=DigestScheduleOut, status_code=status.HTTP_201_CREATED)
def create_schedule(payload: DigestScheduleCreate, _: UserOut = Depends(get_current_user)) -> DigestScheduleOut:
    return DigestScheduleOut(
        id=UUID("14141414-1414-1414-1414-141414141414"),
        workspace_id=payload.workspace_id,
        cron_expression=payload.cron_expression,
        timezone=payload.timezone,
        channel_types=payload.channel_types,
        is_active=payload.is_active,
        created_at=datetime(2026, 3, 10, 9, 35, tzinfo=timezone.utc),
    )


@router.patch("/schedules/{schedule_id}", response_model=DigestScheduleOut)
def update_schedule(
    schedule_id: UUID,
    payload: DigestScheduleUpdate,
    _: UserOut = Depends(get_current_user),
) -> DigestScheduleOut:
    schedule = _get_schedule(schedule_id)
    updates = payload.model_dump(exclude_none=True)
    return schedule.model_copy(update=updates)


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: UUID, _: UserOut = Depends(get_current_user)) -> Response:
    _get_schedule(schedule_id)
    SCHEDULES.pop(schedule_id, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/preview", response_model=DigestOut)
def preview_digest(payload: DigestPreviewRequest, _: UserOut = Depends(get_current_user)) -> DigestOut:
    selected_ids = [
        UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
    ][: payload.limit]
    return DigestOut(
        id=UUID("15151515-1515-1515-1515-151515151515"),
        workspace_id=payload.workspace_id,
        title="Preview Digest",
        period_start=payload.period_start,
        period_end=payload.period_end,
        paper_ids=selected_ids,
        status="draft",
        channel_types=["email"],
        summary_markdown="## Preview\n- Agent systems remain the strongest signal cluster.\n- Robotics content is elevated because of benchmark actionability.",
        created_at=datetime(2026, 3, 10, 9, 40, tzinfo=timezone.utc),
    )


@router.get("/{digest_id}", response_model=DigestOut)
def get_digest(digest_id: UUID, _: UserOut = Depends(get_current_user)) -> DigestOut:
    return _get_digest(digest_id)
