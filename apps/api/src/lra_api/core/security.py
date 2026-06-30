"""Authentication and token utilities."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from lra_api.core.config import get_settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class TokenError(ValueError):
    """Raised for invalid authentication tokens."""


def hash_password(password: str) -> str:
    """Hash password for storage."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, additional_claims: dict[str, Any] | None = None) -> str:
    """Create signed short-lived access token."""
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.app_access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expires_at, "typ": "access"}
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, settings.app_secret_key, algorithm="HS256")


def create_refresh_token(subject: str) -> tuple[str, datetime]:
    """Create signed refresh token with expiry timestamp."""
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(days=settings.app_refresh_token_expire_days)
    payload: dict[str, Any] = {"sub": subject, "exp": expires_at, "typ": "refresh"}
    token = jwt.encode(payload, settings.app_secret_key, algorithm="HS256")
    return token, expires_at


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    """Decode token and validate type claim."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.app_secret_key, algorithms=["HS256"])
    except jwt.InvalidTokenError as exc:
        raise TokenError("Invalid token") from exc

    if payload.get("typ") != expected_type:
        raise TokenError("Invalid token type")

    return payload
