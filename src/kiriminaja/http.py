from __future__ import annotations

from typing import Any
from urllib.parse import urlencode, urljoin

import httpx

from .config import Config


class HttpClient:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._client = config.http_client or httpx.Client()

    def close(self) -> None:
        if self._config.http_client is None:
            self._client.close()

    # -- low-level --------------------------------------------------------

    def request_json(
        self,
        path: str,
        *,
        method: str = "POST",
        body: Any = None,
        query: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        url = self._build_url(path, query)
        req_headers = self._build_headers(body, method, headers)
        content: bytes | None = None
        if body is not None and method not in ("GET", "DELETE"):
            import json as _json

            content = _json.dumps(body).encode()

        response = self._client.request(
            method, url, content=content, headers=req_headers
        )
        if not (200 <= response.status_code < 300):
            raise Exception(
                f"Request failed: {response.status_code} {response.reason_phrase}"
            )
        return response.json()

    def post_json(self, path: str, body: Any = None) -> Any:
        return self.request_json(path, method="POST", body=body)

    def get_json(self, path: str) -> Any:
        return self.request_json(path, method="GET")

    def delete_json(self, path: str) -> Any:
        return self.request_json(path, method="DELETE")

    # -- helpers -----------------------------------------------------------

    def _build_url(self, path: str, query: dict[str, str] | None) -> str:
        base = self._config.resolved_base_url()
        if not path.startswith("/"):
            path = "/" + path
        url = base + path
        if query:
            url += "?" + urlencode(query)
        return url

    def _build_headers(
        self,
        body: Any,
        method: str,
        extra: dict[str, str] | None,
    ) -> dict[str, str]:
        h: dict[str, str] = {"Accept": "application/json"}
        if body is not None and method not in ("GET", "DELETE"):
            h["Content-Type"] = "application/json"
        if self._config.api_key:
            h["Authorization"] = f"Bearer {self._config.api_key}"
        if extra:
            h.update(extra)
        return h


class AsyncHttpClient:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._client = config.async_http_client or httpx.AsyncClient()

    async def aclose(self) -> None:
        if self._config.async_http_client is None:
            await self._client.aclose()

    # -- low-level --------------------------------------------------------

    async def request_json(
        self,
        path: str,
        *,
        method: str = "POST",
        body: Any = None,
        query: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        url = self._build_url(path, query)
        req_headers = self._build_headers(body, method, headers)
        content: bytes | None = None
        if body is not None and method not in ("GET", "DELETE"):
            import json as _json

            content = _json.dumps(body).encode()

        response = await self._client.request(
            method, url, content=content, headers=req_headers
        )
        if not (200 <= response.status_code < 300):
            raise Exception(
                f"Request failed: {response.status_code} {response.reason_phrase}"
            )
        return response.json()

    async def post_json(self, path: str, body: Any = None) -> Any:
        return await self.request_json(path, method="POST", body=body)

    async def get_json(self, path: str) -> Any:
        return await self.request_json(path, method="GET")

    async def delete_json(self, path: str) -> Any:
        return await self.request_json(path, method="DELETE")

    # -- helpers (same as sync) --------------------------------------------

    def _build_url(self, path: str, query: dict[str, str] | None) -> str:
        base = self._config.resolved_base_url()
        if not path.startswith("/"):
            path = "/" + path
        url = base + path
        if query:
            url += "?" + urlencode(query)
        return url

    def _build_headers(
        self,
        body: Any,
        method: str,
        extra: dict[str, str] | None,
    ) -> dict[str, str]:
        h: dict[str, str] = {"Accept": "application/json"}
        if body is not None and method not in ("GET", "DELETE"):
            h["Content-Type"] = "application/json"
        if self._config.api_key:
            h["Authorization"] = f"Bearer {self._config.api_key}"
        if extra:
            h.update(extra)
        return h
