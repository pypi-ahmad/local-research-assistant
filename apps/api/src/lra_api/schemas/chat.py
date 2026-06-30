"""Chat and RAG schema definitions."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatCreateRequest(BaseModel):
    """Create chat session request."""

    notebook_id: UUID
    title: str = Field(min_length=1, max_length=255)


class ChatMessageRequest(BaseModel):
    """Send message request."""

    query: str = Field(min_length=1)
    top_k: int = Field(default=6, ge=1, le=20)


class CitationPayload(BaseModel):
    """Citation representation."""

    document_id: str
    chunk_id: str
    quote: str
    source_name: str
    page_number: int | None = None


class ChatMessageResponse(BaseModel):
    """Assistant response payload."""

    answer: str
    citations: list[CitationPayload]


class MessageResponse(BaseModel):
    """Persisted message output."""

    id: UUID
    role: str
    content: str
    citations_json: list[dict[str, str]]
    created_at: datetime

    model_config = {"from_attributes": True}
