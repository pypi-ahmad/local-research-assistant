"""Health check endpoints."""

from __future__ import annotations

import redis.asyncio as redis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.api.deps import get_current_user
from lra_api.core.config import get_settings
from lra_api.db.models import User
from lra_api.db.session import get_db_session
from lra_api.schemas.system import HealthResponse
from lra_api.services.ollama.client import OllamaClient

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> HealthResponse:
    """Check health of database, redis, and ollama."""
    _ = current_user
    settings = get_settings()

    database = "ok"
    redis_state = "ok"
    ollama = "ok"

    try:
        await db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        database = "error"

    redis_client = redis.from_url(settings.redis_url)
    try:
        await redis_client.ping()
    except Exception:  # noqa: BLE001
        redis_state = "error"
    finally:
        await redis_client.aclose()

    client = OllamaClient()
    try:
        await client.list_models()
    except Exception:  # noqa: BLE001
        ollama = "error"
    finally:
        await client.close()

    status_value = "ok" if database == redis_state == ollama == "ok" else "degraded"
    return HealthResponse(status=status_value, database=database, redis=redis_state, ollama=ollama)
