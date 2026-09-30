from __future__ import annotations

import asyncio
import json
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from ..config import settings


class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float] | None: ...


class DisabledEmbeddingProvider:
    async def embed(self, text: str) -> list[float] | None:
        return None


@dataclass
class OpenAICompatibleEmbeddingProvider:
    endpoint: str
    model: str
    api_key: str = ""

    async def embed(self, text: str) -> list[float] | None:
        return await asyncio.to_thread(self._embed_sync, text)

    def _embed_sync(self, text: str) -> list[float] | None:
        body = json.dumps({"model": self.model, "input": text}).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(self.endpoint, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        data = payload.get("data")
        if not isinstance(data, list) or not data:
            return None
        embedding = data[0].get("embedding") if isinstance(data[0], dict) else None
        if not isinstance(embedding, list) or not embedding:
            return None
        return [float(value) for value in embedding]


def build_embedding_provider() -> EmbeddingProvider:
    if not settings.semantic_search_configured:
        return DisabledEmbeddingProvider()
    return OpenAICompatibleEmbeddingProvider(
        endpoint=settings.embedding_url,
        model=settings.embedding_model,
        api_key=settings.embedding_api_key,
    )
