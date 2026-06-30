# RAG Guide

## What
Hybrid Retrieval-Augmented Generation with citation grounding.

## Why
Pure semantic retrieval can miss exact terminology. Pure keyword search can miss semantic context. Hybrid retrieval improves evidence quality.

## How
1. Query embedding via `qwen3-embedding:4b`.
2. Vector retrieval from Qdrant.
3. Lexical retrieval from Postgres FTS (`to_tsvector/plainto_tsquery`).
4. Score fusion and optional cross-encoder rerank.
5. Context assembly and constrained generation prompt.
6. Citation payload attached to every answer.

## Anti-Hallucination Rules
- If no sufficient evidence found, return insufficient-evidence response.
- Answer prompt explicitly instructs model to use provided evidence only.
- Citations linked to chunk and source metadata.

## Performance Tips
- Reduce `top_k` for lower latency.
- Disable reranker for low-end CPU mode.
- Keep chunk size around 700-1200 chars for balanced recall.

