"""Document schema definitions."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """Document response payload."""

    id: UUID
    notebook_id: UUID
    source_type: str
    original_filename: str
    mime_type: str
    size_bytes: int
    indexing_status: str
    metadata_json: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ImportRequest(BaseModel):
    """Source import request payload."""

    notebook_id: UUID
    source_url: str = Field(min_length=3)


class IngestionJobResponse(BaseModel):
    """Ingestion job status payload."""

    job_id: str
    document_id: UUID | None = None
    status: str
