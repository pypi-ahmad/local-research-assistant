"""Celery background tasks."""

from __future__ import annotations

import asyncio
import uuid

from celery.utils.log import get_task_logger
from lra_api.db.session import AsyncSessionLocal
from lra_api.services.ingestion.pipeline import IngestionService
from lra_api.workers.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="lra_api.workers.tasks.process_document_upload")
def process_document_upload(document_id: str) -> None:
    """Background post-processing task for uploaded document."""

    async def _run() -> None:
        async with AsyncSessionLocal() as db:
            service = IngestionService()
            try:
                await service.process_document(db=db, document_id=uuid.UUID(document_id))
            except ValueError:
                logger.warning("document-not-found", document_id=document_id)

    asyncio.run(_run())
