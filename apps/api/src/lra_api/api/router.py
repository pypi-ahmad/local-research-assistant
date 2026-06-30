"""Primary API router assembly."""

from __future__ import annotations

from fastapi import APIRouter

from lra_api.api.v1.endpoints import (
    auth,
    chat,
    documents,
    graph,
    health,
    knowledge,
    notebooks,
    research,
    search,
    study,
    system,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(notebooks.router, prefix="/notebooks", tags=["notebooks"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(study.router, prefix="/study", tags=["study"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
