"""Notebook schema definitions."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NotebookCreate(BaseModel):
    """Notebook create payload."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class NotebookUpdate(BaseModel):
    """Notebook update payload."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] | None = None
    archived: bool | None = None


class NotebookResponse(BaseModel):
    """Notebook response payload."""

    id: UUID
    title: str
    description: str | None
    tags: list[str]
    archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
