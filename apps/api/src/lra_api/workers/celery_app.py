"""Celery app configuration for ingestion jobs."""

from __future__ import annotations

from celery import Celery

from lra_api.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "lra_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["lra_api.workers.tasks"],
)

celery_app.conf.task_routes = {
    "lra_api.workers.tasks.process_document_upload": {"queue": "celery"},
}
