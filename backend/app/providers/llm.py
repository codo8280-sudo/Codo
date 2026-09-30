from __future__ import annotations

import asyncio
import json
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from ..config import settings


class LlmProvider(Protocol):
    async def answer_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any] | None: ...


class DisabledLlmProvider:
    async def answer_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
        return None


@dataclass
class OpenAICompatibleLlmProvider:
    endpoint: str
    model: str
    api_key: str = ""

    async def answer_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
        return await asyncio.to_thread(self._answer_sync, system_prompt, user_prompt)

    def _answer_sync(self, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            return None
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            return None
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else None


def build_llm_provider() -> LlmProvider:
    if not settings.llm_configured:
        return DisabledLlmProvider()
    return OpenAICompatibleLlmProvider(
        endpoint=settings.llm_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
    )
