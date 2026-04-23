from __future__ import annotations

import json as _json
from typing import Any
from urllib.parse import urlencode

from .config import Config
from .transport import (
    AsyncHttpTransport,
    HttpTransport,
    adapt_async_transport,
    adapt_sync_transport,
)


class HttpError(Exception):
    """Raised when the API responds with a non-2xx status."""

    def __init__(self, status_code: int, reason: str, body: bytes) -> None:
        super().__init__(f"Request failed: {status_code} {reason}")
        self.status_code = status_code
        self.reason = reason
        self.body = body


class HttpClient:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._transport: HttpTransport = adapt_sync_transport(config.http_client)
        self._owns_client = config.http_client is None

    def close(self) -> None:
        if not self._owns_client:
            return
        client = getattr(self._transport, "_client", None) or getattr(
            self._transport, "_session", None
        )
        close = getattr(client, "close", None)
        if callable(close):
            close()

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
            content = _json.dumps(body).encode()

        response = self._transport.request(
            method, url, headers=req_headers, content=content
        )
        if not (200 <= response.status_code < 300):
            raise HttpError(response.status_code, response.reason, response.content)
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
        self._transport: AsyncHttpTransport = adapt_async_transport(
            config.async_http_client
        )
        self._owns_client = config.async_http_client is None

    async def aclose(self) -> None:
        if not self._owns_client:
            return
        client = getattr(self._transport, "_client", None) or getattr(
            self._transport, "_session", None
        )
        aclose = getattr(client, "aclose", None) or getattr(client, "close", None)
        if callable(aclose):
            result = aclose()
            if hasattr(result, "__await__"):
                await result

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
            content = _json.dumps(body).encode()

        response = await self._transport.request(
            method, url, headers=req_headers, content=content
        )
        if not (200 <= response.status_code < 300):
            raise HttpError(response.status_code, response.reason, response.content)
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
