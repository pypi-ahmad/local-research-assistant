# Local Research Assistant

Privacy-first, local-first AI research workspace (NotebookLM-style) using local Ollama models, local vector DB, and local relational storage.

## Live Verification (Real Run)
Verified on **June 30, 2026** with real services and real model calls.

Primary artifact from successful end-to-end run:
- `/tmp/lra-verify/live/live_e2e_summary.json`

Result snapshot from that run:
- Notebook: `ca2e23cb-72bd-447c-8d68-0726295fc19b`
- Ingestion statuses: `note/pdf/image/website/github/youtube = SUCCESS`
- OCR endpoint output length: `5428`
- Retrieval: `search_hits=1`, `chat_citations=1`, `rag_citations=1`
- Conversation memory: `chat_messages=4`
- Study outputs: `quiz_bundles=1`, `flashcards=0`
- Graph: `nodes=2`, `edges=13`
- Health: `database=ok`, `redis=ok`, `ollama=ok`
- Qdrant points: `151`
- OpenAPI paths: `40`
- Bad upload handling: `400/400/400/404` for empty/unsupported/oversize/invalid-notebook

Database count artifact from the same run:
- `/tmp/lra-verify/live/postgres_counts.csv`

## What Is Implemented

- PDF ingestion
- Generic document upload ingestion
- YouTube transcript ingestion
- Website ingestion
- GitHub repository ingestion
- Image/scanned-note ingestion with OCR fallback
- OCR endpoint
- Vector indexing (Qdrant)
- Hybrid retrieval (semantic + lexical)
- Question answering with citations
- Document comparison
- Quiz generation
- Flashcard APIs (implemented; run produced zero cards for this notebook)
- Conversation memory in chat sessions
- Notebook/session handling
- Frontend document upload page and chat page
- Backend REST API with OpenAPI
- Database persistence (Postgres)
- Error handling for invalid uploads

Not implemented:
- Mind map generation endpoint/UI was not found in codebase.

## Architecture

- `apps/api`: FastAPI API + services + Celery tasks
- `apps/web`: React + Vite frontend
- Postgres: metadata, chats, citations, study artifacts
- Redis: queue broker/result backend + app caching/health probes
- Qdrant: embeddings/vector search
- Neo4j: graph entities/relations
- MinIO: raw/derived document storage
- Ollama: embeddings, chat, OCR generation

## Prerequisites

- Linux
- Docker + Docker Compose
- `uv` (Python package/runtime management)
- Python `3.12.x`
- Node.js + npm
- Local Ollama server with required models

## Zero-to-Hero Setup

### 1) Clone and install dependencies

```bash
cd /home/ahmad/AI/local-research-assistant

uv venv --python 3.12
source .venv/bin/activate
UV_CACHE_DIR=.uv-cache-temp uv sync --group dev

cd apps/web
npm install --no-audit --no-fund
cd ../..
```

### 2) Start infrastructure

```bash
docker compose up -d postgres redis qdrant neo4j minio prometheus grafana
```

### 3) Configure environment

Create `.env` from `.env.example` and set correct ports/URLs for your machine.
Default compose ports in this repo:
- Postgres `15432`
- Redis `16379`
- Qdrant `16333`
- Neo4j `17687`
- MinIO `19000`

### 4) Run database migrations

```bash
source .venv/bin/activate
UV_CACHE_DIR=.uv-cache-temp uv run alembic -c apps/api/alembic.ini upgrade head
```

### 5) Bootstrap first admin (one-time)

```bash
curl -sS -X POST "http://127.0.0.1:18000/api/v1/auth/bootstrap" \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@local-research.ai","password":"StrongPassword123!"}'
```

### 6) Start backend API

Default port:
```bash
source .venv/bin/activate
UV_CACHE_DIR=.uv-cache-temp uv run uvicorn lra_api.main:app --host 127.0.0.1 --port 18000
```

Conflict-safe port used in verified run:
```bash
source .venv/bin/activate
export PYTHONPATH=/home/ahmad/AI/local-research-assistant/apps/api/src
uvicorn lra_api.main:app --host 127.0.0.1 --port 28001
```

### 7) Start worker

Recommended stable command (used for successful verification):
```bash
source .venv/bin/activate
export PYTHONPATH=/home/ahmad/AI/local-research-assistant/apps/api/src
celery -A lra_api.workers.celery_app worker --loglevel=INFO --pool=solo --concurrency=1
```

### 8) Start frontend

Default:
```bash
cd apps/web
npm run dev
```

Verified run command (bound to live API):
```bash
cd apps/web
VITE_API_BASE_URL=http://127.0.0.1:28001/api/v1 npm run dev -- --host 127.0.0.1 --port 13100
```

## Verified Commands for Ingestion, Search, Chat, Frontend

### Backend ingestion (upload)

```bash
curl -sS -X POST "http://127.0.0.1:28001/api/v1/documents/upload/<NOTEBOOK_ID>" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/path/to/file.pdf"
```

### Backend ingestion (website/github/youtube)

```bash
curl -sS -X POST "http://127.0.0.1:28001/api/v1/documents/import/website" \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{"notebook_id":"<NOTEBOOK_ID>","source_url":"https://example.com"}'

curl -sS -X POST "http://127.0.0.1:28001/api/v1/documents/import/github" \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{"notebook_id":"<NOTEBOOK_ID>","source_url":"https://github.com/octocat/Hello-World"}'

curl -sS -X POST "http://127.0.0.1:28001/api/v1/documents/import/youtube" \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{"notebook_id":"<NOTEBOOK_ID>","source_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### OCR endpoint

```bash
curl -sS -X POST "http://127.0.0.1:28001/api/v1/documents/ocr" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/path/to/image.png"
```

### Hybrid search

```bash
curl -sS -X POST "http://127.0.0.1:28001/api/v1/search/query" \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{"query":"Bengaluru hybrid retrieval latency optimization","notebook_id":"<NOTEBOOK_ID>","top_k":8}'
```

### Chat (session + grounded answers)

```bash
curl -sS -X POST "http://127.0.0.1:28001/api/v1/chat/sessions" \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{"notebook_id":"<NOTEBOOK_ID>","title":"Research Session"}'

curl -sS -X POST "http://127.0.0.1:28001/api/v1/chat/sessions/<CHAT_ID>/messages" \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{"query":"Which systems are used for semantic and lexical retrieval?","top_k":6}'
```

## Real E2E Workflow Executed

Validated real pipeline:
- upload -> parse/OCR -> chunk/embed/index -> search retrieval -> grounded chat answer -> research summary/compare -> study generation -> graph query

The exact run was automated with:
- `/tmp/lra-verify/run_live_e2e.sh`

Outputs stored in:
- `/tmp/lra-verify/live/`

## Verification and Quality Commands

```bash
source .venv/bin/activate
python -m compileall apps/api/src/lra_api/services/ingestion/pipeline.py
UV_CACHE_DIR=.uv-cache-temp uv run pytest apps/api/tests/unit apps/api/tests/integration -q

cd apps/web
npm run build
```

## API Reference

- Swagger: `http://127.0.0.1:28001/docs`
- OpenAPI JSON: `http://127.0.0.1:28001/openapi.json`

## Runtime Notes from Real Verification

- Ollama latency can dominate end-to-end runtime, especially `generate` calls.
- For stable local verification on busy machines, `celery --pool=solo --concurrency=1` was most reliable.
- Port conflicts happened during verification; alternate ports (`28001`, `13101`) were used successfully.

## Code Fixes Applied During Verification

- `apps/web/src/services/api.ts`: frontend API base URL now respects `VITE_API_BASE_URL`.
- `apps/web/src/pages/ChatPage.tsx`: stream URL now uses env-based API base URL.
- `apps/api/src/lra_api/services/ingestion/parsers.py`: image sources bypass parser and defer to OCR fallback.
- `apps/api/src/lra_api/services/ollama/client.py`: retry/backoff for transient Ollama request failures.
- `apps/api/src/lra_api/services/retrieval/service.py`: filtered stale semantic hits against live DB chunks/docs before citation persistence.
- `apps/api/src/lra_api/services/ingestion/pipeline.py`: bounded OCR timeout fallback; capped OCR text length to bound embedding latency.

