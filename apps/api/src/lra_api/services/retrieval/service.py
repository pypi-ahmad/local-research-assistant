"""Hybrid retrieval and RAG orchestration service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any
from typing import TYPE_CHECKING
from uuid import UUID

from qdrant_client import QdrantClient
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.core.config import get_settings
from lra_api.db.models import Document
from lra_api.db.models import DocumentChunk
from lra_api.schemas.search import SearchHit
from lra_api.services.monitoring.metrics import RETRIEVAL_LATENCY
from lra_api.services.ollama.client import OllamaClient

if TYPE_CHECKING:
    from sentence_transformers import CrossEncoder


@dataclass
class RetrievalResult:
    """Internal retrieval score record."""

    chunk_id: str
    document_id: str
    source_name: str
    text: str
    semantic_score: float
    lexical_score: float
    page_number: int | None
    metadata: dict[str, Any]


class RetrievalService:
    """Hybrid semantic + keyword retrieval service."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.qdrant = QdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
            timeout=30,
            check_compatibility=False,
        )
        self.reranker: CrossEncoder | None = None
        if self.settings.reranker_enabled:
            try:
                from sentence_transformers import CrossEncoder

                self.reranker = CrossEncoder(self.settings.reranker_model, local_files_only=True)
            except Exception:  # noqa: BLE001
                self.reranker = None

    async def search(
        self,
        db: AsyncSession,
        query: str,
        notebook_id: str | None,
        top_k: int,
        source_types: list[str],
        date_from: date | None,
        date_to: date | None,
    ) -> list[SearchHit]:
        """Run hybrid retrieval and rerank results."""
        with RETRIEVAL_LATENCY.time():
            semantic = await self._semantic_search(query, top_k)
            lexical = await self._lexical_search(
                db,
                query,
                notebook_id,
                top_k,
                source_types,
                date_from,
                date_to,
            )

            merged = self._merge_scores(semantic, lexical)
            filtered = await self._filter_existing_chunks(
                db=db,
                results=merged,
                notebook_id=notebook_id,
                source_types=source_types,
                date_from=date_from,
                date_to=date_to,
            )
            reranked = self._rerank(query, filtered)
            return [
                SearchHit(
                    chunk_id=item.chunk_id,
                    document_id=item.document_id,
                    score=round(item.semantic_score + item.lexical_score, 6),
                    lexical_score=round(item.lexical_score, 6),
                    semantic_score=round(item.semantic_score, 6),
                    text=item.text,
                    source_name=item.source_name,
                    page_number=item.page_number,
                    metadata=item.metadata,
                )
                for item in reranked[:top_k]
            ]

    async def build_answer(self, query: str, hits: list[SearchHit]) -> tuple[str, list[dict[str, Any]]]:
        """Build grounded answer and citations from retrieval context."""
        if not hits:
            return (
                "Insufficient evidence in indexed sources. Upload more sources or widen filters.",
                [],
            )

        context_blocks = []
        for idx, hit in enumerate(hits, start=1):
            context_blocks.append(
                f"[{idx}] Source={hit.source_name} Chunk={hit.chunk_id}\n{hit.text}"
            )

        prompt = (
            "Answer user question using only evidence below. "
            "If evidence missing, explicitly say insufficient evidence. "
            "Cite sources with bracket numbers.\n\n"
            f"Question: {query}\n\n"
            "Evidence:\n"
            + "\n\n".join(context_blocks)
        )

        ollama = OllamaClient()
        response = await ollama.generate(prompt=prompt, task="chat", stream=False)
        await ollama.close()
        answer_text = response.get("response", "")

        citations = [
            {
                "document_id": hit.document_id,
                "chunk_id": hit.chunk_id,
                "quote": hit.text[:500],
                "source_name": hit.source_name,
                "page_number": hit.page_number,
            }
            for hit in hits[:6]
        ]
        return answer_text, citations

    async def _semantic_search(self, query: str, top_k: int) -> list[RetrievalResult]:
        ollama = OllamaClient()
        vector = await ollama.embed(query)
        await ollama.close()

        if hasattr(self.qdrant, "query_points"):
            query_response = self.qdrant.query_points(
                collection_name=self.settings.qdrant_collection,
                query=vector,
                limit=top_k * 3,
                with_payload=True,
            )
            points = list(query_response.points)
        else:
            points = self.qdrant.search(
                collection_name=self.settings.qdrant_collection,
                query_vector=vector,
                limit=top_k * 3,
                with_payload=True,
            )

        results: list[RetrievalResult] = []
        for point in points:
            payload = point.payload or {}
            results.append(
                RetrievalResult(
                    chunk_id=str(payload.get("chunk_id", point.id)),
                    document_id=str(payload.get("document_id", "")),
                    source_name=str(payload.get("source_name", "unknown")),
                    text=str(payload.get("text", "")),
                    semantic_score=float(point.score),
                    lexical_score=0.0,
                    page_number=payload.get("page_number"),
                    metadata={"source": "semantic"},
                )
            )
        return results

    async def _lexical_search(
        self,
        db: AsyncSession,
        query: str,
        notebook_id: str | None,
        top_k: int,
        source_types: list[str],
        date_from: date | None,
        date_to: date | None,
    ) -> list[RetrievalResult]:
        filter_clauses = ["d.indexing_status = 'indexed'"]
        params: dict[str, Any] = {"query": query, "limit": top_k * 3}

        if notebook_id is not None:
            filter_clauses.append("d.notebook_id = :notebook_id")
            params["notebook_id"] = notebook_id

        if source_types:
            filter_clauses.append("d.source_type = ANY(:source_types)")
            params["source_types"] = source_types

        if date_from is not None:
            filter_clauses.append("d.created_at >= :date_from")
            params["date_from"] = date_from

        if date_to is not None:
            filter_clauses.append("d.created_at <= :date_to")
            params["date_to"] = date_to

        sql = f"""
            SELECT
                dc.id AS chunk_id,
                d.id AS document_id,
                d.original_filename AS source_name,
                dc.text,
                ts_rank_cd(to_tsvector('english', dc.text), plainto_tsquery('english', :query)) AS lexical_score
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE {' AND '.join(filter_clauses)}
              AND to_tsvector('english', dc.text) @@ plainto_tsquery('english', :query)
            ORDER BY lexical_score DESC
            LIMIT :limit
        """

        result = await db.execute(text(sql), params)
        rows = result.mappings().all()
        return [
            RetrievalResult(
                chunk_id=str(row["chunk_id"]),
                document_id=str(row["document_id"]),
                source_name=str(row["source_name"]),
                text=str(row["text"]),
                semantic_score=0.0,
                lexical_score=float(row["lexical_score"]),
                page_number=None,
                metadata={"source": "lexical"},
            )
            for row in rows
        ]

    def _merge_scores(
        self,
        semantic: list[RetrievalResult],
        lexical: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        merged: dict[str, RetrievalResult] = {}

        for item in semantic:
            merged[item.chunk_id] = item

        for item in lexical:
            if item.chunk_id in merged:
                merged[item.chunk_id].lexical_score = item.lexical_score
                merged[item.chunk_id].metadata["source"] = "hybrid"
            else:
                merged[item.chunk_id] = item

        return sorted(merged.values(), key=lambda x: (x.semantic_score + x.lexical_score), reverse=True)

    def _rerank(self, query: str, results: list[RetrievalResult]) -> list[RetrievalResult]:
        if self.reranker is None or not results:
            return results

        pairs = [(query, item.text) for item in results]
        scores = self.reranker.predict(pairs)
        rescored = []
        for item, score in zip(results, scores, strict=True):
            item.semantic_score += float(score)
            rescored.append(item)
        return sorted(rescored, key=lambda x: (x.semantic_score + x.lexical_score), reverse=True)

    async def _filter_existing_chunks(
        self,
        db: AsyncSession,
        results: list[RetrievalResult],
        notebook_id: str | None,
        source_types: list[str],
        date_from: date | None,
        date_to: date | None,
    ) -> list[RetrievalResult]:
        """Drop stale vector hits and align payload with live relational rows."""
        if not results:
            return []

        chunk_ids: list[UUID] = []
        for result in results:
            try:
                chunk_ids.append(UUID(result.chunk_id))
            except ValueError:
                continue

        if not chunk_ids:
            return []

        stmt = (
            select(
                DocumentChunk.id.label("chunk_id"),
                Document.id.label("document_id"),
                Document.original_filename.label("source_name"),
                DocumentChunk.text.label("chunk_text"),
                DocumentChunk.page_number.label("page_number"),
            )
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(
                DocumentChunk.id.in_(chunk_ids),
                Document.indexing_status == "indexed",
            )
        )

        if notebook_id is not None:
            try:
                stmt = stmt.where(Document.notebook_id == UUID(notebook_id))
            except ValueError:
                return []

        if source_types:
            stmt = stmt.where(Document.source_type.in_(source_types))

        if date_from is not None:
            stmt = stmt.where(Document.created_at >= date_from)

        if date_to is not None:
            stmt = stmt.where(Document.created_at <= date_to)

        rows = (await db.execute(stmt)).all()
        by_chunk = {str(row.chunk_id): row for row in rows}

        filtered: list[RetrievalResult] = []
        for item in results:
            row = by_chunk.get(item.chunk_id)
            if row is None:
                continue
            item.document_id = str(row.document_id)
            item.source_name = str(row.source_name)
            item.text = str(row.chunk_text)
            item.page_number = row.page_number
            filtered.append(item)

        return filtered
