"""Study tools endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.api.deps import get_current_user
from lra_api.db.models import Flashcard, Notebook, Quiz, StudyMaterial, User
from lra_api.db.session import get_db_session
from lra_api.schemas.study import StudyGenerateRequest, StudyResponse
from lra_api.services.study.service import StudyService

router = APIRouter()


@router.post("/generate", response_model=StudyResponse)
async def generate_study_assets(
    payload: StudyGenerateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> StudyResponse:
    """Generate study guide, flashcards, and quiz content."""
    notebook_result = await db.execute(
        select(Notebook).where(Notebook.id == payload.notebook_id, Notebook.owner_id == current_user.id)
    )
    notebook = notebook_result.scalar_one_or_none()
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")

    service = StudyService()
    study = await service.generate(str(payload.notebook_id), payload.topic, payload.difficulty)

    material = StudyMaterial(
        notebook_id=payload.notebook_id,
        kind="study_bundle",
        title=f"{payload.topic} ({payload.difficulty})",
        content_json=study.model_dump(mode="json"),
    )
    db.add(material)
    await db.flush()

    for item in study.flashcards:
        db.add(Flashcard(study_material_id=material.id, front=item.front, back=item.back))

    db.add(
        Quiz(
            study_material_id=material.id,
            questions_json=[question.model_dump() for question in study.quiz],
        )
    )

    await db.commit()
    return study


@router.get("/flashcards/{notebook_id}")
async def list_flashcards(
    notebook_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, str]]:
    """List flashcards for notebook."""
    result = await db.execute(
        select(Flashcard.front, Flashcard.back)
        .join(StudyMaterial, StudyMaterial.id == Flashcard.study_material_id)
        .join(Notebook, Notebook.id == StudyMaterial.notebook_id)
        .where(Notebook.id == notebook_id, Notebook.owner_id == current_user.id)
    )
    return [{"front": row.front, "back": row.back} for row in result.all()]


@router.get("/quizzes/{notebook_id}")
async def list_quizzes(
    notebook_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[list[dict[str, str]]]:
    """List quiz payloads for notebook."""
    result = await db.execute(
        select(Quiz.questions_json)
        .join(StudyMaterial, StudyMaterial.id == Quiz.study_material_id)
        .join(Notebook, Notebook.id == StudyMaterial.notebook_id)
        .where(Notebook.id == notebook_id, Notebook.owner_id == current_user.id)
    )
    return [row.questions_json for row in result.all()]
