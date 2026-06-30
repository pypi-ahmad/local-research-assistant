"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.api.deps import get_current_user
from lra_api.db.models import User
from lra_api.db.session import get_db_session
from lra_api.schemas.auth import (
    BootstrapRequest,
    LoginRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserResponse,
)
from lra_api.services.auth.service import AuthService

router = APIRouter()


@router.post("/bootstrap", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def bootstrap_admin(
    payload: BootstrapRequest,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Create initial admin account once."""
    user = await AuthService.bootstrap_admin(db, payload.email, payload.password)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db_session)) -> TokenResponse:
    """Login user and issue tokens."""
    return await AuthService.login(db, payload.email, payload.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Refresh access token."""
    return await AuthService.refresh(db, payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Logout and revoke refresh token."""
    await AuthService.logout(db, payload.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return current authenticated user."""
    return UserResponse.model_validate(current_user)
