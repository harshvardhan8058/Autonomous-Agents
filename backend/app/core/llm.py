"""Minimal async LLM client (OpenAI-compatible chat completions).

Handwritten on purpose: one dependency (httpx), one retry policy,
no framework abstractions to debug in production.
"""
from typing import Any

import httpx

from app.core.config import LLMSettings
from app.utils.json_utils import LLMJSONError, extract_json


class LLMClient:
    def __init__(self, settings: LLMSettings) -> None:
        self._settings = settings

    async def complete(
        self, system: str, user: str, temperature: float = 0.3
    ) -> str:
        async with httpx.AsyncClient(timeout=self._settings.timeout) as client:
            response = await client.post(
                f"{self._settings.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._settings.api_key}"},
                json={
                    "model": self._settings.model,
                    "temperature": temperature,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def complete_json(
        self, system: str, user: str, temperature: float = 0.2
    ) -> dict[str, Any]:
        """Structured completion. Retries malformed JSON exactly once."""
        raw = await self.complete(system, user, temperature)
        try:
            return extract_json(raw)
        except LLMJSONError:
            repair = (
                "Your previous reply was not valid JSON. "
                "Return ONLY the corrected JSON object, no prose.\n\n"
                f"Previous reply:\n{raw}"
            )
            raw = await self.complete(system, repair, temperature=0.0)
            return extract_json(raw)  # second failure propagates as 502
