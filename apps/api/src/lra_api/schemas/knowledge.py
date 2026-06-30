"""Knowledge organization schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class HighlightRequest(BaseModel):
    """Highlight create request."""

    document_id: UUID
    chunk_id: UUID | None = None
    text: str = Field(min_length=1)
    color: str = "yellow"


class AnnotationRequest(BaseModel):
    """Annotation create request."""

    document_id: UUID
    chunk_id: UUID | None = None
    note: str = Field(min_length=1)


class FolderRequest(BaseModel):
    """Folder create payload."""

    name: str = Field(min_length=1, max_length=255)


class CollectionRequest(BaseModel):
    """Collection create payload."""

    notebook_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class BookmarkRequest(BaseModel):
    """Bookmark create payload."""

    document_id: UUID
    chunk_id: UUID | None = None
    label: str = Field(min_length=1, max_length=255)


class NoteRequest(BaseModel):
    """Research note create payload."""

    notebook_id: UUID
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
