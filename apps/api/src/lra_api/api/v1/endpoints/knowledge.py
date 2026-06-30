"""Knowledge organization endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.api.deps import get_current_user
from lra_api.db.models import (
    Annotation,
    Bookmark,
    Collection,
    Document,
    Folder,
    Highlight,
    Notebook,
    Note,
    User,
)
from lra_api.db.session import get_db_session
from lra_api.schemas.knowledge import (
    AnnotationRequest,
    BookmarkRequest,
    CollectionRequest,
    FolderRequest,
    HighlightRequest,
    NoteRequest,
)

router = APIRouter()


@router.post("/folders", status_code=status.HTTP_201_CREATED)
async def create_folder(
    payload: FolderRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Create notebook folder."""
    folder = Folder(owner_id=current_user.id, name=payload.name)
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return {"folder_id": str(folder.id)}


@router.get("/folders")
async def list_folders(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, str]]:
    """List folders for current user."""
    result = await db.execute(select(Folder).where(Folder.owner_id == current_user.id))
    folders = result.scalars().all()
    return [{"id": str(folder.id), "name": folder.name} for folder in folders]


@router.post("/collections", status_code=status.HTTP_201_CREATED)
async def create_collection(
    payload: CollectionRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Create notebook-scoped collection."""
    await _assert_notebook_ownership(db, payload.notebook_id, current_user.id)
    collection = Collection(
        notebook_id=payload.notebook_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return {"collection_id": str(collection.id)}


@router.get("/collections")
async def list_collections(
    notebook_id: UUID | None = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, str]]:
    """List collections for user notebooks."""
    query = (
        select(Collection)
        .join(Notebook, Notebook.id == Collection.notebook_id)
        .where(Notebook.owner_id == current_user.id)
    )
    if notebook_id is not None:
        query = query.where(Collection.notebook_id == notebook_id)
    result = await db.execute(query.order_by(Collection.created_at.desc()))
    collections = result.scalars().all()
    return [
        {
            "id": str(collection.id),
            "notebook_id": str(collection.notebook_id),
            "name": collection.name,
            "description": collection.description or "",
        }
        for collection in collections
    ]


@router.post("/bookmarks", status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    payload: BookmarkRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Create source bookmark."""
    await _assert_document_ownership(db, payload.document_id, current_user.id)
    bookmark = Bookmark(
        user_id=current_user.id,
        document_id=payload.document_id,
        chunk_id=payload.chunk_id,
        label=payload.label,
    )
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    return {"bookmark_id": str(bookmark.id)}


@router.get("/bookmarks")
async def list_bookmarks(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, str]]:
    """List user bookmarks."""
    result = await db.execute(select(Bookmark).where(Bookmark.user_id == current_user.id))
    bookmarks = result.scalars().all()
    return [
        {
            "id": str(bookmark.id),
            "document_id": str(bookmark.document_id),
            "label": bookmark.label,
        }
        for bookmark in bookmarks
    ]


@router.post("/notes", status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Create notebook research note."""
    await _assert_notebook_ownership(db, payload.notebook_id, current_user.id)
    note = Note(notebook_id=payload.notebook_id, title=payload.title, content=payload.content)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return {"note_id": str(note.id)}


@router.get("/notes")
async def list_notes(
    notebook_id: UUID | None = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, str]]:
    """List notebook notes for current user."""
    query = select(Note).join(Notebook, Notebook.id == Note.notebook_id).where(Notebook.owner_id == current_user.id)
    if notebook_id is not None:
        query = query.where(Note.notebook_id == notebook_id)
    result = await db.execute(query.order_by(Note.updated_at.desc()))
    notes = result.scalars().all()
    return [
        {
            "id": str(note.id),
            "notebook_id": str(note.notebook_id),
            "title": note.title,
            "content": note.content,
        }
        for note in notes
    ]


@router.post("/highlights", status_code=status.HTTP_201_CREATED)
async def create_highlight(
    payload: HighlightRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Create document highlight."""
    await _assert_document_ownership(db, payload.document_id, current_user.id)
    highlight = Highlight(
        document_id=payload.document_id,
        chunk_id=payload.chunk_id,
        text=payload.text,
        color=payload.color,
    )
    db.add(highlight)
    await db.commit()
    await db.refresh(highlight)
    return {"highlight_id": str(highlight.id)}


@router.post("/annotations", status_code=status.HTTP_201_CREATED)
async def create_annotation(
    payload: AnnotationRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Create annotation linked to source chunk/document."""
    await _assert_document_ownership(db, payload.document_id, current_user.id)
    annotation = Annotation(document_id=payload.document_id, chunk_id=payload.chunk_id, note=payload.note)
    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)
    return {"annotation_id": str(annotation.id)}


@router.get("/highlights")
async def list_highlights(
    document_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, str]]:
    """List highlights for user's accessible documents."""
    query = (
        select(Highlight)
        .join(Document, Document.id == Highlight.document_id)
        .join(Notebook, Notebook.id == Document.notebook_id)
        .where(Notebook.owner_id == current_user.id)
    )
    if document_id is not None:
        query = query.where(Document.id == document_id)

    result = await db.execute(query.order_by(Highlight.created_at.desc()))
    highlights = result.scalars().all()
    return [
        {
            "id": str(highlight.id),
            "document_id": str(highlight.document_id),
            "text": highlight.text,
            "color": highlight.color,
        }
        for highlight in highlights
    ]


@router.get("/annotations")
async def list_annotations(
    document_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, str]]:
    """List annotations for user's accessible documents."""
    query = (
        select(Annotation)
        .join(Document, Document.id == Annotation.document_id)
        .join(Notebook, Notebook.id == Document.notebook_id)
        .where(Notebook.owner_id == current_user.id)
    )
    if document_id is not None:
        query = query.where(Document.id == document_id)

    result = await db.execute(query.order_by(Annotation.created_at.desc()))
    annotations = result.scalars().all()
    return [
        {
            "id": str(annotation.id),
            "document_id": str(annotation.document_id),
            "note": annotation.note,
        }
        for annotation in annotations
    ]


async def _assert_document_ownership(db: AsyncSession, document_id: UUID, user_id: UUID) -> None:
    result = await db.execute(
        select(Document.id)
        .join(Notebook, Notebook.id == Document.notebook_id)
        .where(Document.id == document_id, Notebook.owner_id == user_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


async def _assert_notebook_ownership(db: AsyncSession, notebook_id: UUID, user_id: UUID) -> None:
    result = await db.execute(select(Notebook.id).where(Notebook.id == notebook_id, Notebook.owner_id == user_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
