"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from lra_api.api.router import api_router
from lra_api.core.config import get_settings
from lra_api.core.logging import setup_logging
from lra_api.core.rate_limit import RateLimiter
from lra_api.services.monitoring.metrics import REQUEST_COUNTER, metrics_router
from lra_api.services.storage.minio_service import MinioStorageService

settings = get_settings()
if settings.app_env != "testing":
    setup_logging()
rate_limiter = RateLimiter()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Local privacy-first AI research assistant API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.app_allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(metrics_router)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request counts by endpoint, method, and response status."""
    await rate_limiter.enforce(request)
    response = await call_next(request)
    REQUEST_COUNTER.labels(
        endpoint=request.url.path,
        method=request.method,
        status=str(response.status_code),
    ).inc()
    return response


@app.on_event("startup")
async def startup_event() -> None:
    """Prepare storage buckets and service prerequisites."""
    if settings.app_env == "testing":
        return
    try:
        storage = MinioStorageService()
        storage.ensure_buckets()
    except Exception:  # noqa: BLE001
        # Service might not be available during local bootstrap.
        return


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Close shared clients on shutdown."""
    await rate_limiter.close()


@app.get("/health/live", tags=["health"])
async def liveness() -> dict[str, str]:
    """Container liveness endpoint."""
    return {"status": "alive"}
