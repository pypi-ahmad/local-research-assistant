"""System and monitoring schemas."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health payload."""

    status: str
    database: str
    redis: str
    ollama: str


class ModelInfo(BaseModel):
    """Local model metadata."""

    name: str
    size: str
    modified: str


class SystemStatusResponse(BaseModel):
    """Runtime health and resource payload."""

    cpu_percent: float
    memory_percent: float
    gpu_utilization: float | None
    gpu_memory_used_mb: float | None
    queue_depth: int
