"""Hybrid search endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.api.deps import get_current_user
from lra_api.db.models import SearchHistory, User
from lra_api.db.session import get_db_session
from lra_api.schemas.search import SearchRequest, SearchResponse
from lra_api.services.retrieval.service import RetrievalService

router = APIRouter()


@router.post("/query", response_model=SearchResponse)
async def query_search(
    payload: SearchRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> SearchResponse:
    """Run hybrid semantic + keyword search."""
    retrieval = RetrievalService()
    hits = await retrieval.search(
        db=db,
        query=payload.query,
        notebook_id=str(payload.notebook_id) if payload.notebook_id else None,
        top_k=payload.top_k,
        source_types=payload.source_types,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )

    history = SearchHistory(
        user_id=current_user.id,
        notebook_id=payload.notebook_id,
        query=payload.query,
        result_count=len(hits),
    )
    db.add(history)
    await db.commit()

    return SearchResponse(query=payload.query, hits=hits)
