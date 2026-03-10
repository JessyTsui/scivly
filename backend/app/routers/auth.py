from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status

from app.schemas.auth import (
    AuthCallbackRequest,
    AuthCallbackResponse,
    LoginRequest,
    LoginResponse,
    UserOut,
)
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_202_ACCEPTED)
def login(payload: LoginRequest) -> LoginResponse:
    return LoginResponse(
        message=f"Login link queued for {payload.email}.",
        redirect_url="https://app.scivly.dev/auth/callback?source=mock",
    )


@router.post("/callback", response_model=AuthCallbackResponse)
def callback(payload: AuthCallbackRequest, current_user: UserOut = Depends(get_current_user)) -> AuthCallbackResponse:
    return AuthCallbackResponse(
        access_token=f"scivly_access_{payload.code[-6:]}",
        refresh_token="scivly_refresh_mocktoken",
        issued_at=datetime(2026, 3, 10, 8, 30, tzinfo=timezone.utc),
        user=current_user,
    )


@router.get("/me", response_model=UserOut)
def me(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    return current_user
