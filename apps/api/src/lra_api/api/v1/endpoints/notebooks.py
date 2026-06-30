"""Notebook endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.api.deps import get_current_user
from lra_api.db.models import Notebook, User
from lra_api.db.session import get_db_session
from lra_api.schemas.notebook import NotebookCreate, NotebookResponse, NotebookUpdate

router = APIRouter()


@router.post("", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    payload: NotebookCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> NotebookResponse:
    """Create notebook for authenticated user."""
    notebook = Notebook(
        owner_id=current_user.id,
        title=payload.title,
        description=payload.description,
        tags=payload.tags,
    )
    db.add(notebook)
    await db.commit()
    await db.refresh(notebook)
    return NotebookResponse.model_validate(notebook)


@router.get("", response_model=list[NotebookResponse])
async def list_notebooks(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[NotebookResponse]:
    """List notebooks for authenticated user."""
    result = await db.execute(select(Notebook).where(Notebook.owner_id == current_user.id))
    notebooks = result.scalars().all()
    return [NotebookResponse.model_validate(notebook) for notebook in notebooks]


@router.patch("/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: UUID,
    payload: NotebookUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> NotebookResponse:
    """Update notebook metadata."""
    result = await db.execute(
        select(Notebook).where(Notebook.id == notebook_id, Notebook.owner_id == current_user.id)
    )
    notebook = result.scalar_one_or_none()
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(notebook, key, value)

    await db.commit()
    await db.refresh(notebook)
    return NotebookResponse.model_validate(notebook)


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete notebook and cascade resources."""
    result = await db.execute(
        select(Notebook).where(Notebook.id == notebook_id, Notebook.owner_id == current_user.id)
    )
    notebook = result.scalar_one_or_none()
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")

    await db.delete(notebook)
    await db.commit()
