# Installation Guide

## Prerequisites
- Linux/macOS/Windows with Docker Desktop or Docker Engine.
- Python `3.12.10`.
- Node `24+`.
- Local Ollama installed and running (`ollama serve`).

## 1. Clone and Configure

```bash
git clone <your-repo-url> local-research-assistant
cd local-research-assistant
cp .env.example .env
```

## 2. Python Environment (uv)

```bash
UV_CACHE_DIR=.uv-cache-temp uv venv --python 3.12.10
source .venv/bin/activate
UV_CACHE_DIR=.uv-cache-temp uv sync --group dev
```

## 3. Frontend Dependencies

```bash
cd apps/web
npm install
cd ../..
```

## 4. Start Infrastructure

```bash
docker compose up -d postgres redis qdrant neo4j minio prometheus grafana
```

## 5. Run Migrations

```bash
source .venv/bin/activate
uv run alembic -c apps/api/alembic.ini upgrade head
```

## 6. Start Services

Terminal A:
```bash
source .venv/bin/activate
uv run uvicorn lra_api.main:app --host 0.0.0.0 --port 18000 --reload
```

Terminal B:
```bash
source .venv/bin/activate
uv run celery -A lra_api.workers.celery_app.celery_app worker -l info
```

Terminal C:
```bash
cd apps/web
npm run dev
```

## 7. Bootstrap First User

```bash
./infra/scripts/bootstrap_admin.sh admin@example.com 'StrongPassword123!'
```

