"""Search and retrieval schema definitions."""

from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Hybrid search request."""

    query: str = Field(min_length=2)
    notebook_id: UUID | None = None
    top_k: int = Field(default=8, ge=1, le=50)
    metadata_filters: dict[str, Any] = Field(default_factory=dict)
    source_types: list[str] = Field(default_factory=list)
    date_from: date | None = None
    date_to: date | None = None


class SearchHit(BaseModel):
    """Search result hit with source metadata."""

    chunk_id: str
    document_id: str
    score: float
    lexical_score: float
    semantic_score: float
    text: str
    source_name: str
    page_number: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Search response payload."""

    query: str
    hits: list[SearchHit]
