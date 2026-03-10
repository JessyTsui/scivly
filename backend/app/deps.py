from collections.abc import Iterator

from fastapi import Query, Request

from app.config import Settings, get_settings
from app.middleware.error_handler import APIError
from app.schemas.auth import UserOut


class PaginationParams:
    def __init__(self, page: int, per_page: int) -> None:
        self.page = page
        self.per_page = per_page


def get_settings_dep() -> Settings:
    return get_settings()


def get_db() -> Iterator[None]:
    yield None


def get_current_user(request: Request) -> UserOut:
    current_user = getattr(request.state, "current_user", None)
    if current_user is None:
        raise APIError(status_code=401, code="unauthorized", message="Authentication context is missing.")
    return current_user


def get_pagination_params(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
) -> PaginationParams:
    return PaginationParams(page=page, per_page=per_page)
