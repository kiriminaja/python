from __future__ import annotations

from typing import Any, List

from ..http import AsyncHttpClient, HttpClient


class CourierService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def list(self) -> Any:
        return self._client.post_json("/api/mitra/couriers")

    def group(self) -> Any:
        return self._client.post_json("/api/mitra/couriers_group")

    def detail(self, courier_code: str) -> Any:
        return self._client.post_json(
            "/api/mitra/courier_services", {"courier_code": courier_code}
        )

    def set_whitelist_services(self, services: List[str]) -> Any:
        return self._client.post_json(
            "/api/mitra/v3/set_whitelist_services", {"services": services}
        )


class AsyncCourierService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def list(self) -> Any:
        return await self._client.post_json("/api/mitra/couriers")

    async def group(self) -> Any:
        return await self._client.post_json("/api/mitra/couriers_group")

    async def detail(self, courier_code: str) -> Any:
        return await self._client.post_json(
            "/api/mitra/courier_services", {"courier_code": courier_code}
        )

    async def set_whitelist_services(self, services: List[str]) -> Any:
        return await self._client.post_json(
            "/api/mitra/v3/set_whitelist_services", {"services": services}
        )
