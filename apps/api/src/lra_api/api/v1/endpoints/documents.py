"""Document ingestion endpoints."""

from __future__ import annotations

from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.api.deps import get_current_user
from lra_api.db.models import Document, Notebook, User
from lra_api.db.session import get_db_session
from lra_api.schemas.document import DocumentResponse, ImportRequest, IngestionJobResponse
from lra_api.services.ingestion.connectors import ConnectorService
from lra_api.services.ingestion.pipeline import IngestionService
from lra_api.services.ollama.client import OllamaClient
from lra_api.utils.uploads import validate_upload
from lra_api.workers.tasks import process_document_upload

router = APIRouter()


@router.post("/upload/{notebook_id}", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    notebook_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> IngestionJobResponse:
    """Upload file and queue ingestion/indexing task."""
    notebook_result = await db.execute(
        select(Notebook).where(Notebook.id == notebook_id, Notebook.owner_id == current_user.id)
    )
    notebook = notebook_result.scalar_one_or_none()
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    try:
        validate_upload(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    ingestion = IngestionService()
    document = await ingestion.ingest_upload(db, notebook_id=notebook_id, filename=file.filename, content=content)

    task = process_document_upload.delay(str(document.id))
    return IngestionJobResponse(job_id=task.id, document_id=document.id, status="queued")


@router.post("/import/website", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_website(
    payload: ImportRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> IngestionJobResponse:
    """Import website content and queue indexing."""
    await _assert_notebook_access(db, payload.notebook_id, current_user.id)
    connector = ConnectorService()
    filename, content = await connector.fetch_website_text(payload.source_url)
    ingestion = IngestionService()
    document = await ingestion.ingest_upload(db, payload.notebook_id, filename, content)
    task = process_document_upload.delay(str(document.id))
    return IngestionJobResponse(job_id=task.id, document_id=document.id, status="queued")


@router.post("/import/github", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_github(
    payload: ImportRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> IngestionJobResponse:
    """Import GitHub repository text content."""
    await _assert_notebook_access(db, payload.notebook_id, current_user.id)
    connector = ConnectorService()
    filename, content = await connector.fetch_github_repo_snapshot(payload.source_url)
    ingestion = IngestionService()
    document = await ingestion.ingest_upload(db, payload.notebook_id, filename, content)
    task = process_document_upload.delay(str(document.id))
    return IngestionJobResponse(job_id=task.id, document_id=document.id, status="queued")


@router.post("/import/youtube", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_youtube(
    payload: ImportRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> IngestionJobResponse:
    """Import YouTube transcript content."""
    await _assert_notebook_access(db, payload.notebook_id, current_user.id)
    connector = ConnectorService()
    filename, content = await connector.fetch_youtube_transcript(payload.source_url)
    ingestion = IngestionService()
    document = await ingestion.ingest_upload(db, payload.notebook_id, filename, content)
    task = process_document_upload.delay(str(document.id))
    return IngestionJobResponse(job_id=task.id, document_id=document.id, status="queued")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """Get document metadata."""
    result = await db.execute(
        select(Document)
        .join(Notebook, Notebook.id == Document.notebook_id)
        .where(Document.id == document_id, Notebook.owner_id == current_user.id)
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(document)


@router.get("/jobs/{job_id}", response_model=IngestionJobResponse)
async def get_ingestion_job(job_id: str) -> IngestionJobResponse:
    """Return task queue status."""
    result = AsyncResult(job_id)
    return IngestionJobResponse(job_id=job_id, status=result.status)


@router.post("/ocr")
async def run_ocr(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Run OCR on uploaded image or scanned page using local model."""
    _ = current_user
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

    ollama = OllamaClient()
    text = await ollama.ocr_image(content, filename=file.filename)
    await ollama.close()
    return {"text": text}


async def _assert_notebook_access(db: AsyncSession, notebook_id: UUID, user_id: UUID) -> None:
    result = await db.execute(select(Notebook.id).where(Notebook.id == notebook_id, Notebook.owner_id == user_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
