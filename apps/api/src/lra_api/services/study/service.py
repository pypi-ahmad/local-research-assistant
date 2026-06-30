"""Study material generation service."""

from __future__ import annotations

import json

from lra_api.schemas.study import FlashcardItem, QuizItem, StudyResponse
from lra_api.services.ollama.client import OllamaClient


class StudyService:
    """Generate study assets from notebook context and topic."""

    async def generate(self, notebook_id: str, topic: str, difficulty: str) -> StudyResponse:
        """Generate study guide, flashcards, and quiz content."""
        prompt = (
            "Create JSON with keys study_guide, flashcards, quiz. "
            "flashcards list items with front/back. "
            "quiz list items with question/options/answer. "
            f"Topic: {topic}. Difficulty: {difficulty}."
        )

        ollama = OllamaClient()
        raw = await ollama.generate(prompt=prompt, task="study", stream=False)
        await ollama.close()
        text = raw.get("response", "{}")

        payload: dict[str, object]
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {
                "study_guide": text,
                "flashcards": [],
                "quiz": [],
            }

        flashcards = [FlashcardItem(**item) for item in payload.get("flashcards", []) if isinstance(item, dict)]
        quiz = [QuizItem(**item) for item in payload.get("quiz", []) if isinstance(item, dict)]
        study_guide = str(payload.get("study_guide", text))

        return StudyResponse(
            notebook_id=notebook_id,
            topic=topic,
            difficulty=difficulty,
            study_guide=study_guide,
            flashcards=flashcards,
            quiz=quiz,
        )
