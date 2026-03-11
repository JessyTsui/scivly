from fastapi import APIRouter, Depends

from app.config import Settings
from app.db import get_database_status
from app.deps import get_settings_dep
from app.schemas.common import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health(settings: Settings = Depends(get_settings_dep)) -> HealthResponse:
    return HealthResponse(status="ok", version=settings.app_version)


@router.get("/ready", response_model=ReadyResponse, summary="Readiness check")
async def ready(settings: Settings = Depends(get_settings_dep)) -> ReadyResponse:
    return ReadyResponse(
        status="ok",
        version=settings.app_version,
        checks={
            "config": "ok",
            "routers": "ok",
            "auth_middleware": "ok",
            "database": await get_database_status(),
        },
    )
