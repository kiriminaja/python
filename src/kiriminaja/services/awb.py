from __future__ import annotations

from typing import Any

from ..http import AsyncHttpClient, HttpClient


class AWBService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def print(self, payload: dict[str, Any]) -> Any:
        return self._client.post_json("/api/mitra/v6.1/awb/print", payload)


class AsyncAWBService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def print(self, payload: dict[str, Any]) -> Any:
        return await self._client.post_json("/api/mitra/v6.1/awb/print", payload)
