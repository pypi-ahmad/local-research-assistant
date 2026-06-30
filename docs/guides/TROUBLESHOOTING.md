# Troubleshooting Guide

## API cannot start
- Check `.env` values.
- Verify Postgres and Redis containers are healthy.
- Run `uv run alembic -c apps/api/alembic.ini upgrade head`.

## OCR empty output
- Confirm `glm-ocr` installed (`ollama list`).
- Use clearer/high-resolution image.

## Slow retrieval
- Reduce `top_k`.
- Disable reranker (`RERANKER_ENABLED=false`).
- Verify Qdrant container has enough memory.

## No citations
- Check document indexing status is `indexed`.
- Ensure search query actually matches corpus.

## Frontend CORS error
- Add web origin in `APP_ALLOWED_ORIGINS`.

