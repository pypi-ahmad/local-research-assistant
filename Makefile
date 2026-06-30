SHELL := /bin/bash

.PHONY: setup install web-install up down migrate api worker web test lint typecheck e2e

setup:
	UV_CACHE_DIR=.uv-cache-temp uv venv --python 3.12.10
	source .venv/bin/activate && UV_CACHE_DIR=.uv-cache-temp uv sync --group dev

web-install:
	cd apps/web && npm install

up:
	docker compose up -d

down:
	docker compose down

migrate:
	source .venv/bin/activate && uv run alembic -c apps/api/alembic.ini upgrade head

api:
	source .venv/bin/activate && uv run uvicorn lra_api.main:app --host 0.0.0.0 --port 18000 --reload

worker:
	source .venv/bin/activate && uv run celery -A lra_api.workers.celery_app.celery_app worker -l info

web:
	cd apps/web && npm run dev

test:
	source .venv/bin/activate && uv run pytest apps/api/tests/unit apps/api/tests/integration

lint:
	source .venv/bin/activate && uv run ruff check .

typecheck:
	source .venv/bin/activate && uv run mypy apps/api/src

e2e:
	cd apps/web && npm run test:e2e
