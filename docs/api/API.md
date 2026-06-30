# API Documentation

OpenAPI UI: `http://localhost:18000/docs`

## Auth
- `POST /api/v1/auth/bootstrap`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

## Notebooks
- `POST /api/v1/notebooks`
- `GET /api/v1/notebooks`
- `PATCH /api/v1/notebooks/{notebook_id}`
- `DELETE /api/v1/notebooks/{notebook_id}`

## Documents + OCR
- `POST /api/v1/documents/upload/{notebook_id}`
- `POST /api/v1/documents/import/website`
- `POST /api/v1/documents/import/github`
- `POST /api/v1/documents/import/youtube`
- `GET /api/v1/documents/{document_id}`
- `GET /api/v1/documents/jobs/{job_id}`
- `POST /api/v1/documents/ocr`

## Knowledge Organization
- `POST /api/v1/knowledge/folders`
- `GET /api/v1/knowledge/folders`
- `POST /api/v1/knowledge/collections`
- `GET /api/v1/knowledge/collections`
- `POST /api/v1/knowledge/bookmarks`
- `GET /api/v1/knowledge/bookmarks`
- `POST /api/v1/knowledge/notes`
- `GET /api/v1/knowledge/notes`
- `POST /api/v1/knowledge/highlights`
- `GET /api/v1/knowledge/highlights`
- `POST /api/v1/knowledge/annotations`
- `GET /api/v1/knowledge/annotations`

## Search + RAG + Chat
- `POST /api/v1/search/query`
- `POST /api/v1/chat/rag`
- `POST /api/v1/chat/sessions`
- `POST /api/v1/chat/sessions/{chat_id}/messages`
- `POST /api/v1/chat/sessions/{chat_id}/stream`

## Research Features
- `POST /api/v1/research/summary`
- `POST /api/v1/research/compare`
- `POST /api/v1/research/timeline`
- `POST /api/v1/research/glossary`
- `POST /api/v1/research/entities`

## Study Tools
- `POST /api/v1/study/generate`
- `GET /api/v1/study/flashcards/{notebook_id}`
- `GET /api/v1/study/quizzes/{notebook_id}`

## Knowledge Graph
- `POST /api/v1/graph/query`

## Health + Observability
- `GET /api/v1/health`
- `GET /health/live`
- `GET /metrics`
- `GET /api/v1/system/models`
- `GET /api/v1/system/status`
