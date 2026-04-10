from __future__ import annotations

from typing import Any

from ..http import AsyncHttpClient, HttpClient


class PickupService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def schedules(self) -> Any:
        return self._client.post_json("/api/mitra/v2/schedules")


class AsyncPickupService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def schedules(self) -> Any:
        return await self._client.post_json("/api/mitra/v2/schedules")
