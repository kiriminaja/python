from __future__ import annotations

from typing import Any

from ..http import AsyncHttpClient, HttpClient


class AddressService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def provinces(self) -> Any:
        return self._client.post_json("/api/mitra/province")

    def cities(self, provinsi_id: int) -> Any:
        return self._client.post_json("/api/mitra/city", {"provinsi_id": provinsi_id})

    def districts(self, kabupaten_id: int) -> Any:
        return self._client.post_json(
            "/api/mitra/kecamatan", {"kabupaten_id": kabupaten_id}
        )

    def sub_districts(self, kecamatan_id: int) -> Any:
        return self._client.post_json(
            "/api/mitra/kelurahan", {"kecamatan_id": kecamatan_id}
        )

    def districts_by_name(self, search: str) -> Any:
        return self._client.post_json(
            "/api/mitra/v2/get_address_by_name", {"search": search}
        )


class AsyncAddressService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def provinces(self) -> Any:
        return await self._client.post_json("/api/mitra/province")

    async def cities(self, provinsi_id: int) -> Any:
        return await self._client.post_json(
            "/api/mitra/city", {"provinsi_id": provinsi_id}
        )

    async def districts(self, kabupaten_id: int) -> Any:
        return await self._client.post_json(
            "/api/mitra/kecamatan", {"kabupaten_id": kabupaten_id}
        )

    async def sub_districts(self, kecamatan_id: int) -> Any:
        return await self._client.post_json(
            "/api/mitra/kelurahan", {"kecamatan_id": kecamatan_id}
        )

    async def districts_by_name(self, search: str) -> Any:
        return await self._client.post_json(
            "/api/mitra/v2/get_address_by_name", {"search": search}
        )
