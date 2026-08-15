"""LiteLLM chat-completions HTTP client (adapter)."""
from typing import Any

import httpx


class LiteLLMClient:
    def __init__(self, base_url: str, master_key: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.master_key = master_key
        self._client = httpx.AsyncClient(timeout=timeout)

    async def chat_completions(self, body: dict[str, Any]) -> dict[str, Any]:
        resp = await self._client.post(
            f"{self.base_url}/v1/chat/completions",
            json=body,
            headers={
                "Authorization": f"Bearer {self.master_key}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def aclose(self) -> None:
        await self._client.aclose()
