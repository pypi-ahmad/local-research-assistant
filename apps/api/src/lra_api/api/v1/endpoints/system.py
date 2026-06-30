"""System monitoring endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from lra_api.api.deps import get_current_user
from lra_api.db.models import User
from lra_api.schemas.system import ModelInfo, SystemStatusResponse
from lra_api.services.monitoring.system import MonitoringService
from lra_api.services.ollama.client import OllamaClient

router = APIRouter()


@router.get("/models", response_model=list[ModelInfo])
async def list_models(current_user: User = Depends(get_current_user)) -> list[ModelInfo]:
    """List local Ollama models."""
    _ = current_user
    client = OllamaClient()
    models = await client.list_models()
    await client.close()

    return [
        ModelInfo(name=model.get("name", ""), size=str(model.get("size", "")), modified=str(model.get("modified_at", "")))
        for model in models
    ]


@router.get("/status", response_model=SystemStatusResponse)
async def system_status(current_user: User = Depends(get_current_user)) -> SystemStatusResponse:
    """Get runtime utilization metrics."""
    _ = current_user
    service = MonitoringService()
    return SystemStatusResponse(**service.system_status())
