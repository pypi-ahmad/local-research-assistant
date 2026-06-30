"""Study asset schema definitions."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class StudyGenerateRequest(BaseModel):
    """Study generation request."""

    notebook_id: UUID
    topic: str = Field(min_length=2)
    difficulty: Literal["beginner", "intermediate", "advanced"] = "intermediate"


class FlashcardItem(BaseModel):
    """Flashcard item."""

    front: str
    back: str


class QuizItem(BaseModel):
    """Quiz item."""

    question: str
    options: list[str]
    answer: str


class StudyResponse(BaseModel):
    """Study generation output."""

    notebook_id: UUID
    topic: str
    difficulty: str
    study_guide: str
    flashcards: list[FlashcardItem]
    quiz: list[QuizItem]
