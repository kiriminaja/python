from __future__ import annotations

from typing import Any

from ..http import AsyncHttpClient, HttpClient


class CalculationsService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def cod(self, payload: dict[str, Any]) -> Any:
        return self._client.post_json("/api/mitra/calculations/cod", payload)


class AsyncCalculationsService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def cod(self, payload: dict[str, Any]) -> Any:
        return await self._client.post_json("/api/mitra/calculations/cod", payload)
