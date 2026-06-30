"""Research analysis endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from lra_api.api.deps import get_current_user
from lra_api.db.models import User
from lra_api.schemas.research import CompareRequest, ResearchOutput, SummaryRequest
from lra_api.services.research.service import ResearchService

router = APIRouter()


@router.post("/summary", response_model=ResearchOutput)
async def summarize(
    payload: SummaryRequest,
    current_user: User = Depends(get_current_user),
) -> ResearchOutput:
    """Generate document or chapter summary."""
    _ = current_user
    service = ResearchService()
    return ResearchOutput(content=await service.summarize(payload.text, payload.mode))


@router.post("/compare", response_model=ResearchOutput)
async def compare(
    payload: CompareRequest,
    current_user: User = Depends(get_current_user),
) -> ResearchOutput:
    """Compare two documents and detect contradictions."""
    _ = current_user
    service = ResearchService()
    return ResearchOutput(content=await service.compare(payload.text_a, payload.text_b))


@router.post("/timeline", response_model=ResearchOutput)
async def timeline(
    payload: SummaryRequest,
    current_user: User = Depends(get_current_user),
) -> ResearchOutput:
    """Generate timeline from source text."""
    _ = current_user
    service = ResearchService()
    return ResearchOutput(content=await service.timeline(payload.text))


@router.post("/glossary", response_model=ResearchOutput)
async def glossary(
    payload: SummaryRequest,
    current_user: User = Depends(get_current_user),
) -> ResearchOutput:
    """Generate glossary from source text."""
    _ = current_user
    service = ResearchService()
    return ResearchOutput(content=await service.glossary(payload.text))


@router.post("/entities", response_model=ResearchOutput)
async def entities(
    payload: SummaryRequest,
    current_user: User = Depends(get_current_user),
) -> ResearchOutput:
    """Extract entities and relationships from source text."""
    _ = current_user
    service = ResearchService()
    return ResearchOutput(content=await service.entities(payload.text))
