"""Knowledge graph endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from lra_api.api.deps import get_current_user
from lra_api.db.models import User
from lra_api.schemas.graph import GraphQueryRequest, GraphResponse
from lra_api.services.graph.service import GraphService

router = APIRouter()


@router.post("/query", response_model=GraphResponse)
async def query_graph(
    payload: GraphQueryRequest,
    current_user: User = Depends(get_current_user),
) -> GraphResponse:
    """Query knowledge graph entities and relations."""
    _ = current_user
    graph_service = GraphService()
    try:
        result = graph_service.query(payload.query, payload.limit)
    finally:
        graph_service.close()

    return GraphResponse(nodes=result["nodes"], edges=result["edges"])
