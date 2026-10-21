from __future__ import annotations

from typing import Any, List
from urllib.parse import urlparse

from ..http import AsyncHttpClient, HttpClient


def _validate_callback_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("callback_url must be an absolute HTTP or HTTPS URL")


class PreferenceService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def set_whitelist_services(self, services: List[str]) -> Any:
        return self._client.post_json(
            "/api/mitra/v3/set_whitelist_services", {"services": services}
        )

    def set_callback(self, callback_url: str) -> Any:
        _validate_callback_url(callback_url)
        return self._client.post_json(
            "/api/mitra/set_callback", {"url": callback_url}
        )


class AsyncPreferenceService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def set_whitelist_services(self, services: List[str]) -> Any:
        return await self._client.post_json(
            "/api/mitra/v3/set_whitelist_services", {"services": services}
        )

    async def set_callback(self, callback_url: str) -> Any:
        _validate_callback_url(callback_url)
        return await self._client.post_json(
            "/api/mitra/set_callback", {"url": callback_url}
        )
