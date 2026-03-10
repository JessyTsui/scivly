from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.deps import PaginationParams, get_current_user, get_pagination_params
from app.middleware.error_handler import APIError
from app.schemas.auth import UserOut
from app.schemas.common import PaginatedResponse
from app.schemas.interest import (
    AuthorWatchlistCreate,
    AuthorWatchlistOut,
    AuthorWatchlistUpdate,
    TopicProfileCreate,
    TopicProfileOut,
    TopicProfileUpdate,
)

router = APIRouter(prefix="/interests", tags=["Interests"])

TOPIC_PROFILES = {
    UUID("55555555-5555-5555-5555-555555555555"): TopicProfileOut(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        workspace_id=UUID("22222222-2222-2222-2222-222222222222"),
        name="Agentic LLM Systems",
        categories=["cs.AI", "cs.CL"],
        keywords=["tool use", "agents", "long-context"],
        is_default=True,
        created_at=datetime(2026, 2, 19, 7, 45, tzinfo=timezone.utc),
    ),
    UUID("66666666-6666-6666-6666-666666666666"): TopicProfileOut(
        id=UUID("66666666-6666-6666-6666-666666666666"),
        workspace_id=UUID("22222222-2222-2222-2222-222222222222"),
        name="Vision-Language Robotics",
        categories=["cs.RO", "cs.CV"],
        keywords=["vision-language-action", "robotics", "policy learning"],
        is_default=False,
        created_at=datetime(2026, 2, 24, 12, 0, tzinfo=timezone.utc),
    ),
}

AUTHOR_WATCHLISTS = {
    UUID("77777777-7777-7777-7777-777777777777"): AuthorWatchlistOut(
        id=UUID("77777777-7777-7777-7777-777777777777"),
        workspace_id=UUID("22222222-2222-2222-2222-222222222222"),
        author_name="Chelsea Finn",
        arxiv_author_id="finn_c_1",
        notes="Robotics and adaptation signals.",
        created_at=datetime(2026, 2, 23, 5, 10, tzinfo=timezone.utc),
    )
}


def _paginate(items: list[TopicProfileOut] | list[AuthorWatchlistOut], params: PaginationParams) -> PaginatedResponse:
    start = (params.page - 1) * params.per_page
    end = start + params.per_page
    return PaginatedResponse(
        items=items[start:end],
        total=len(items),
        page=params.page,
        per_page=params.per_page,
    )


def _get_profile(profile_id: UUID) -> TopicProfileOut:
    profile = TOPIC_PROFILES.get(profile_id)
    if profile is None:
        raise APIError(status_code=404, code="topic_profile_not_found", message="Topic profile not found.")
    return profile


def _get_watchlist(watchlist_id: UUID) -> AuthorWatchlistOut:
    watchlist = AUTHOR_WATCHLISTS.get(watchlist_id)
    if watchlist is None:
        raise APIError(status_code=404, code="author_watchlist_not_found", message="Author watchlist not found.")
    return watchlist


@router.get("/topic-profiles", response_model=PaginatedResponse[TopicProfileOut])
def list_topic_profiles(
    pagination: PaginationParams = Depends(get_pagination_params),
    _: UserOut = Depends(get_current_user),
) -> PaginatedResponse[TopicProfileOut]:
    items = sorted(TOPIC_PROFILES.values(), key=lambda profile: profile.created_at, reverse=True)
    return _paginate(items, pagination)


@router.post("/topic-profiles", response_model=TopicProfileOut, status_code=status.HTTP_201_CREATED)
def create_topic_profile(payload: TopicProfileCreate, current_user: UserOut = Depends(get_current_user)) -> TopicProfileOut:
    return TopicProfileOut(
        id=UUID("88888888-8888-8888-8888-888888888888"),
        workspace_id=current_user.workspace_id,
        name=payload.name,
        categories=payload.categories,
        keywords=payload.keywords,
        is_default=payload.is_default,
        created_at=datetime(2026, 3, 10, 9, 45, tzinfo=timezone.utc),
    )


@router.get("/topic-profiles/{profile_id}", response_model=TopicProfileOut)
def get_topic_profile(profile_id: UUID, _: UserOut = Depends(get_current_user)) -> TopicProfileOut:
    return _get_profile(profile_id)


@router.patch("/topic-profiles/{profile_id}", response_model=TopicProfileOut)
def update_topic_profile(
    profile_id: UUID,
    payload: TopicProfileUpdate,
    _: UserOut = Depends(get_current_user),
) -> TopicProfileOut:
    profile = _get_profile(profile_id)
    updates = payload.model_dump(exclude_none=True)
    return profile.model_copy(update=updates)


@router.delete("/topic-profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic_profile(profile_id: UUID, _: UserOut = Depends(get_current_user)) -> Response:
    _get_profile(profile_id)
    TOPIC_PROFILES.pop(profile_id, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/author-watchlists", response_model=PaginatedResponse[AuthorWatchlistOut])
def list_author_watchlists(
    pagination: PaginationParams = Depends(get_pagination_params),
    _: UserOut = Depends(get_current_user),
) -> PaginatedResponse[AuthorWatchlistOut]:
    items = sorted(AUTHOR_WATCHLISTS.values(), key=lambda watchlist: watchlist.created_at, reverse=True)
    return _paginate(items, pagination)


@router.post("/author-watchlists", response_model=AuthorWatchlistOut, status_code=status.HTTP_201_CREATED)
def create_author_watchlist(
    payload: AuthorWatchlistCreate,
    current_user: UserOut = Depends(get_current_user),
) -> AuthorWatchlistOut:
    return AuthorWatchlistOut(
        id=UUID("99999999-9999-9999-9999-999999999999"),
        workspace_id=current_user.workspace_id,
        author_name=payload.author_name,
        arxiv_author_id=payload.arxiv_author_id,
        notes=payload.notes,
        created_at=datetime(2026, 3, 10, 9, 50, tzinfo=timezone.utc),
    )


@router.get("/author-watchlists/{watchlist_id}", response_model=AuthorWatchlistOut)
def get_author_watchlist(watchlist_id: UUID, _: UserOut = Depends(get_current_user)) -> AuthorWatchlistOut:
    return _get_watchlist(watchlist_id)


@router.patch("/author-watchlists/{watchlist_id}", response_model=AuthorWatchlistOut)
def update_author_watchlist(
    watchlist_id: UUID,
    payload: AuthorWatchlistUpdate,
    _: UserOut = Depends(get_current_user),
) -> AuthorWatchlistOut:
    watchlist = _get_watchlist(watchlist_id)
    updates = payload.model_dump(exclude_none=True)
    return watchlist.model_copy(update=updates)


@router.delete("/author-watchlists/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author_watchlist(watchlist_id: UUID, _: UserOut = Depends(get_current_user)) -> Response:
    _get_watchlist(watchlist_id)
    AUTHOR_WATCHLISTS.pop(watchlist_id, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
