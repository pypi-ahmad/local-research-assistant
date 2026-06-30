"""Prometheus metrics endpoint and helpers."""

from __future__ import annotations

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

metrics_router = APIRouter(tags=["metrics"])

REQUEST_COUNTER = Counter(
    "lra_requests_total",
    "Total requests served",
    ["endpoint", "method", "status"],
)

RETRIEVAL_LATENCY = Histogram(
    "lra_retrieval_latency_seconds",
    "Retrieval latency in seconds",
)


@metrics_router.get("/metrics")
async def metrics() -> Response:
    """Expose Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
