from __future__ import annotations

from typing import Any

from ..http import AsyncHttpClient, HttpClient
from .normalization import normalize_profile


class ProfileService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get(self) -> Any:
        return self._client.get_json("/api/mitra/v6.2/profile")

    def normalized(self) -> dict[str, Any]:
        return normalize_profile(self.get())


class AsyncProfileService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def get(self) -> Any:
        return await self._client.get_json("/api/mitra/v6.2/profile")

    async def normalized(self) -> dict[str, Any]:
        return normalize_profile(await self.get())
