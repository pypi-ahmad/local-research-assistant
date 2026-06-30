"""Application configuration models."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables.

    Example:
        >>> settings = Settings()
        >>> settings.app_name
        'Local Research Assistant'
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_env: Literal["development", "testing", "production"] = "development"
    app_name: str = "Local Research Assistant"
    app_host: str = "0.0.0.0"
    app_port: int = 18000
    app_secret_key: str = "change-me"
    app_access_token_expire_minutes: int = 30
    app_refresh_token_expire_days: int = 7
    app_allowed_origins: Annotated[list[AnyHttpUrl | str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:13000"]
    )

    database_url: str
    sync_database_url: str
    redis_url: str

    qdrant_url: str
    qdrant_api_key: str | None = None
    qdrant_collection: str = "document_chunks"

    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_secure: bool = False
    minio_bucket_raw: str = "raw-documents"
    minio_bucket_derived: str = "derived-artifacts"

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_chat_model: str = "qwen3.5:4b"
    ollama_summary_model: str = "granite4.1:3b"
    ollama_light_model: str = "phi4-mini:3.8b"
    ollama_fallback_model: str = "qwen3.5:2b"
    ollama_embedding_model: str = "qwen3-embedding:4b"
    ollama_ocr_model: str = "glm-ocr"
    ollama_translation_model: str = "translategemma:4b"
    ollama_request_timeout: int = 180

    reranker_model: str = "BAAI/bge-reranker-base"
    reranker_enabled: bool = True

    celery_broker_url: str
    celery_result_backend: str

    prometheus_enabled: bool = True
    enable_gpu_metrics: bool = True

    @field_validator("app_allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> object:
        """Accept comma-separated origins or JSON list from env."""
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                return raw
            return [item.strip() for item in raw.split(",") if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
