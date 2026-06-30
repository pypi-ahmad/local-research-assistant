"""Chunking utilities for document text."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    """Text chunk with metadata."""

    index: int
    text: str
    token_count: int


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[Chunk]:
    """Split text into overlapping chunks by character window.

    Example:
        >>> chunks = chunk_text("hello world" * 200)
        >>> len(chunks) >= 1
        True
    """
    normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not normalized:
        return []

    chunks: list[Chunk] = []
    start = 0
    idx = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        piece = normalized[start:end]
        chunks.append(Chunk(index=idx, text=piece, token_count=max(1, len(piece) // 4)))
        idx += 1
        if end == len(normalized):
            break
        start = max(0, end - overlap)
    return chunks
