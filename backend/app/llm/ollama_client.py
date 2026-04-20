"""Thin local Ollama client adapter."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from urllib import request


@dataclass(frozen=True, slots=True)
class OllamaClient:
    base_url: str = "http://127.0.0.1:11434"
    timeout_seconds: float = 60.0

    async def generate(self, *, model: str, prompt: str) -> str:
        return await asyncio.to_thread(self._generate_sync, model, prompt)

    def _generate_sync(self, model: str, prompt: str) -> str:
        url = f"{self.base_url.rstrip('/')}/api/generate"
        payload = json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
            }
        ).encode("utf-8")
        http_request = request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
        return str(data.get("response", "")).strip()
