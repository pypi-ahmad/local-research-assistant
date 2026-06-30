"""Tests for chunking behavior."""

from lra_api.services.ingestion.chunking import chunk_text


def test_chunk_text_produces_multiple_chunks_with_overlap() -> None:
    text = " ".join(["token"] * 2200)
    chunks = chunk_text(text, chunk_size=1000, overlap=100)

    assert len(chunks) >= 2
    assert chunks[0].index == 0
    assert chunks[1].index == 1
    assert chunks[0].token_count > 0


def test_chunk_text_returns_empty_for_blank_input() -> None:
    chunks = chunk_text(" \n\n ")
    assert chunks == []
