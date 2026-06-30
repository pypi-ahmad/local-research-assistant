"""Simple Redis-backed API rate limiting."""

from __future__ import annotations

import hashlib

import redis.asyncio as redis
from fastapi import HTTPException, Request, status

from lra_api.core.config import get_settings


class RateLimiter:
    """Sliding-window style limiter using Redis counters."""

    def __init__(self, max_requests: int = 120, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        settings = get_settings()
        self.settings = settings
        self.redis = redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)

    async def enforce(self, request: Request) -> None:
        """Apply IP + path scope limit."""
        if self.settings.app_env == "testing":
            return
        client_host = request.client.host if request.client else "unknown"
        digest = hashlib.sha256(f"{client_host}:{request.url.path}".encode()).hexdigest()
        key = f"ratelimit:{digest}"

        try:
            count = await self.redis.incr(key)
            if count == 1:
                await self.redis.expire(key, self.window_seconds)

            if count > self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )
        except Exception:
            # Fail-open for local/offline development if Redis is unavailable.
            return

    async def close(self) -> None:
        """Close redis connection."""
        try:
            await self.redis.aclose()
        except Exception:
            return
