# Search Guide

## Search Modes
- Semantic search: embedding similarity in Qdrant.
- Keyword search: Postgres full-text ranking.
- Hybrid search: fused score + optional reranker.

## Filters
- Notebook filter
- Source type filter
- Date range filter
- Metadata filter payload

## Result Shape
Each hit returns:
- `chunk_id`
- `document_id`
- `source_name`
- lexical + semantic score
- passage text

## Best Practices
- Keep query short and explicit for first pass.
- Use notebook filter to reduce noise.
- For exact terms, include quoted terminology in query text.

