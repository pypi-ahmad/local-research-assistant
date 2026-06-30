"""Research feature schema definitions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    """Summary request payload."""

    text: str = Field(min_length=10)
    mode: str = Field(default="executive")


class CompareRequest(BaseModel):
    """Comparison request payload."""

    text_a: str = Field(min_length=10)
    text_b: str = Field(min_length=10)


class ResearchOutput(BaseModel):
    """Generic research output."""

    content: str
