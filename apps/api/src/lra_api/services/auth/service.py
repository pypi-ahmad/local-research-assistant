"""Authentication service operations."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from lra_api.db.models import RefreshToken, User
from lra_api.schemas.auth import TokenResponse


class AuthService:
    """Authentication domain service."""

    @staticmethod
    async def bootstrap_admin(db: AsyncSession, email: str, password: str) -> User:
        """Create initial admin user when no users exist.

        Example:
            >>> # await AuthService.bootstrap_admin(db, "admin@example.com", "strong-pass")
        """
        existing_users = await db.execute(select(User.id).limit(1))
        if existing_users.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bootstrap already completed")

        user = User(email=email, password_hash=hash_password(password), is_active=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> TokenResponse:
        """Validate credentials and issue access + refresh tokens."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(str(user.id))
        refresh_token, expires_at = create_refresh_token(str(user.id))

        token_record = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
        db.add(token_record)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in_seconds=30 * 60,
        )

    @staticmethod
    async def refresh(db: AsyncSession, refresh_token: str) -> TokenResponse:
        """Rotate refresh token and issue new access token."""
        payload = decode_token(refresh_token, expected_type="refresh")
        result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
        token_record = result.scalar_one_or_none()

        if (
            token_record is None
            or token_record.revoked_at is not None
            or token_record.expires_at < datetime.now(UTC)
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalid")

        user_id = str(payload["sub"])
        access_token = create_access_token(user_id)
        new_refresh_token, expires_at = create_refresh_token(user_id)

        token_record.revoked_at = datetime.now(UTC)
        db.add(
            RefreshToken(
                user_id=token_record.user_id,
                token=new_refresh_token,
                expires_at=expires_at,
            )
        )
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in_seconds=30 * 60,
        )

    @staticmethod
    async def logout(db: AsyncSession, refresh_token: str) -> None:
        """Revoke provided refresh token."""
        result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
        token_record = result.scalar_one_or_none()
        if token_record is not None:
            token_record.revoked_at = datetime.now(UTC)
            await db.commit()
