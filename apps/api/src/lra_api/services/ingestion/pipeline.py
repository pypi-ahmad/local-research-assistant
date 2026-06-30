"""Document ingestion and indexing pipeline."""

from __future__ import annotations

import asyncio
import hashlib
import uuid
from pathlib import Path
from typing import Any

import magic
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.core.config import get_settings
from lra_api.db.models import Document, DocumentChunk, Notebook
from lra_api.services.ingestion.chunking import chunk_text
from lra_api.services.ingestion.parsers import parse_bytes
from lra_api.services.graph.service import GraphService
from lra_api.services.ollama.client import OllamaClient
from lra_api.services.storage.minio_service import MinioStorageService


class IngestionService:
    """Pipeline service for source ingestion, chunking, and indexing."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.storage = MinioStorageService()
        self.qdrant = QdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
            timeout=30,
            check_compatibility=False,
        )

    async def ingest_upload(
        self,
        db: AsyncSession,
        notebook_id: uuid.UUID,
        filename: str,
        content: bytes,
    ) -> Document:
        """Store upload and create queued document metadata."""
        notebook_result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        notebook = notebook_result.scalar_one_or_none()
        if notebook is None:
            raise ValueError("Notebook not found")

        mime_type = magic.from_buffer(content, mime=True)
        storage_key = self._build_storage_key(filename, content)
        self.storage.ensure_buckets()
        self.storage.put_raw_document(storage_key, content, mime_type)

        document = Document(
            notebook_id=notebook_id,
            source_type="upload",
            original_filename=filename,
            storage_key=storage_key,
            mime_type=mime_type,
            size_bytes=len(content),
            metadata_json={},
            indexing_status="queued",
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document

    async def process_document(self, db: AsyncSession, document_id: uuid.UUID) -> Document:
        """Run parse, chunk, embed, and index pipeline for existing document."""
        document_result = await db.execute(select(Document).where(Document.id == document_id))
        document = document_result.scalar_one_or_none()
        if document is None:
            raise ValueError("Document not found")

        document.indexing_status = "processing"
        await db.commit()

        content = self.storage.get_raw_document(document.storage_key)
        text = parse_bytes(content, filename=document.original_filename, mime_type=document.mime_type)
        if not text.strip() and self._requires_ocr(document.original_filename, document.mime_type):
            # Bound OCR latency so image uploads cannot remain stuck in processing indefinitely.
            text = await self._run_ocr_with_timeout(content=content, filename=document.original_filename)
            # Cap OCR payload size to keep embedding latency bounded for scanned/image sources.
            if len(text) > 4000:
                text = text[:4000]
            if not text.strip():
                text = f"Image document: {document.original_filename}"

        chunks = chunk_text(text)
        await self._persist_chunks(db, document, chunks)
        graph_edges = 0
        try:
            graph = GraphService()
            try:
                graph_edges = graph.upsert_document_graph(str(document.id), text)
            finally:
                graph.close()
        except Exception:  # noqa: BLE001
            graph_edges = 0

        document.indexing_status = "indexed"
        document.metadata_json = {
            "chunks": len(chunks),
            "graph_edges": graph_edges,
            "source_extension": Path(document.original_filename).suffix.lower(),
        }
        await db.commit()
        await db.refresh(document)
        return document

    async def _persist_chunks(
        self,
        db: AsyncSession,
        document: Document,
        chunks: list[Any],
    ) -> None:
        ollama = OllamaClient()
        qdrant_points: list[PointStruct] = []
        vector_size = 0

        existing_chunks = await db.execute(select(DocumentChunk).where(DocumentChunk.document_id == document.id))
        for existing in existing_chunks.scalars().all():
            await db.delete(existing)
        await db.flush()

        for chunk in chunks:
            embedding = await ollama.embed(chunk.text)
            if vector_size == 0:
                vector_size = len(embedding)
            chunk_row = DocumentChunk(
                document_id=document.id,
                chunk_index=chunk.index,
                text=chunk.text,
                token_count=chunk.token_count,
                metadata_json={},
            )
            db.add(chunk_row)
            await db.flush()
            qdrant_points.append(
                PointStruct(
                    id=str(chunk_row.id),
                    vector=embedding,
                    payload={
                        "document_id": str(document.id),
                        "chunk_id": str(chunk_row.id),
                        "text": chunk.text,
                        "source_name": document.original_filename,
                    },
                )
            )

        if vector_size:
            await self._ensure_qdrant_collection(vector_size)
        if qdrant_points:
            self.qdrant.upsert(collection_name=self.settings.qdrant_collection, points=qdrant_points)

        await db.commit()
        await ollama.close()

    async def _run_ocr_with_timeout(self, content: bytes, filename: str) -> str:
        """Run OCR with bounded latency and graceful fallback."""
        ollama = OllamaClient()
        try:
            timeout_seconds = max(10, min(int(self.settings.ollama_request_timeout), 90))
            return await asyncio.wait_for(ollama.ocr_image(content, filename=filename), timeout=timeout_seconds)
        except Exception:  # noqa: BLE001
            return ""
        finally:
            await ollama.close()

    async def _ensure_qdrant_collection(self, vector_size: int) -> None:
        existing = self.qdrant.collection_exists(collection_name=self.settings.qdrant_collection)
        if not existing:
            self.qdrant.create_collection(
                collection_name=self.settings.qdrant_collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    @staticmethod
    def _build_storage_key(filename: str, content: bytes) -> str:
        digest = hashlib.sha256(content).hexdigest()
        suffix = Path(filename).suffix
        return f"uploads/{digest}{suffix}"

    @staticmethod
    def _requires_ocr(filename: str, mime_type: str) -> bool:
        suffix = Path(filename).suffix.lower()
        return mime_type.startswith("image/") or suffix in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
            ".pdf",
        }
