"""Knowledge graph schema definitions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GraphQueryRequest(BaseModel):
    """Graph query payload."""

    query: str = Field(min_length=2)
    limit: int = Field(default=50, ge=1, le=500)


class GraphNode(BaseModel):
    """Graph node payload."""

    id: str
    label: str
    kind: str


class GraphEdge(BaseModel):
    """Graph edge payload."""

    source: str
    target: str
    relation: str


class GraphResponse(BaseModel):
    """Graph query response."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]
