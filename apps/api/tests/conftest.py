"""Global test configuration."""

from __future__ import annotations

import os

DEFAULT_ENV = {
    "APP_ENV": "testing",
    "DATABASE_URL": "postgresql+asyncpg://lra:lra_password@localhost:15432/lra",
    "SYNC_DATABASE_URL": "postgresql+psycopg://lra:lra_password@localhost:15432/lra",
    "REDIS_URL": "redis://localhost:16379/0",
    "QDRANT_URL": "http://localhost:16333",
    "NEO4J_URI": "bolt://localhost:17687",
    "NEO4J_USER": "neo4j",
    "NEO4J_PASSWORD": "neo4j_password",
    "MINIO_ENDPOINT": "localhost:19000",
    "MINIO_ACCESS_KEY": "minio",
    "MINIO_SECRET_KEY": "minio_password",
    "CELERY_BROKER_URL": "redis://localhost:16379/1",
    "CELERY_RESULT_BACKEND": "redis://localhost:16379/2",
}

for key, value in DEFAULT_ENV.items():
    os.environ.setdefault(key, value)
