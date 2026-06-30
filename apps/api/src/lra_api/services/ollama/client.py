"""Ollama HTTP client with model routing helpers."""

from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass
from typing import Any

import httpx

from lra_api.core.config import get_settings


@dataclass
class ModelRoute:
    """Task-specific model route."""

    task: str
    model: str


class OllamaClient:
    """Client for local Ollama inference APIs."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = httpx.AsyncClient(base_url=self.settings.ollama_base_url, timeout=self.settings.ollama_request_timeout)

    async def list_models(self) -> list[dict[str, Any]]:
        """Return installed local model metadata."""
        data = await self._request_with_retry("GET", "/api/tags")
        return data.get("models", [])

    async def embed(self, text: str) -> list[float]:
        """Generate embedding vector."""
        payload = await self._request_with_retry(
            "POST",
            "/api/embeddings",
            json={"model": self.settings.ollama_embedding_model, "prompt": text},
        )
        return payload["embedding"]

    async def generate(self, prompt: str, task: str = "chat", stream: bool = False) -> dict[str, Any]:
        """Generate response for routed model task."""
        model_name = self._route_model(task)
        return await self._request_with_retry(
            "POST",
            "/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": stream},
        )

    async def ocr_image(self, image_bytes: bytes, filename: str) -> str:
        """Run OCR prompt over image bytes using local OCR model."""
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        payload = await self._request_with_retry(
            "POST",
            "/api/generate",
            json={
                "model": self.settings.ollama_ocr_model,
                "prompt": f"Extract full text content from image file {filename}. Preserve structure.",
                "images": [encoded],
                "stream": False,
            },
        )
        return payload.get("response", "")

    def _route_model(self, task: str) -> str:
        routes = {
            "chat": self.settings.ollama_chat_model,
            "summary": self.settings.ollama_summary_model,
            "study": self.settings.ollama_summary_model,
            "fast": self.settings.ollama_light_model,
            "fallback": self.settings.ollama_fallback_model,
            "translation": self.settings.ollama_translation_model,
        }
        return routes.get(task, self.settings.ollama_chat_model)

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        retries: int = 4,
    ) -> dict[str, Any]:
        """Issue request with retry on transient network/server failures."""
        last_exc: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                response = await self.client.request(method, path, json=json)
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                last_exc = exc
                status_code = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
                retriable = isinstance(exc, httpx.RequestError) or (status_code is not None and status_code >= 500)
                if (not retriable) or attempt == retries:
                    raise
                await asyncio.sleep(min(2 ** (attempt - 1), 8))
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("ollama-request-failed")
