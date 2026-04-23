"""Framework-agnostic HTTP transport layer.

The KiriminAja SDK does not require any specific HTTP library. Users can:

1. Do nothing — the SDK falls back to the stdlib (``urllib``) for sync calls.
2. Pass an existing client (``httpx.Client``, ``httpx.AsyncClient``,
   ``requests.Session``, ``aiohttp.ClientSession``) — auto-adapted.
3. Pass a custom object implementing :class:`HttpTransport` /
   :class:`AsyncHttpTransport`.

Only the stdlib is required at runtime. ``httpx`` / ``requests`` /
``aiohttp`` are optional and detected lazily.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Protocol, runtime_checkable


@dataclass(slots=True)
class HttpResponse:
    """Minimal response envelope returned by every transport."""

    status_code: int
    headers: Mapping[str, str]
    content: bytes
    reason: str = ""

    def json(self) -> Any:
        if not self.content:
            return None
        return json.loads(self.content)


@runtime_checkable
class HttpTransport(Protocol):
    """Synchronous transport contract.

    Implementations must be safe to call from a synchronous context and
    return an :class:`HttpResponse`. They are responsible for raising on
    network-level failures; HTTP error statuses are handled by the SDK.
    """

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        content: Optional[bytes],
    ) -> HttpResponse: ...


@runtime_checkable
class AsyncHttpTransport(Protocol):
    """Asynchronous transport contract."""

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        content: Optional[bytes],
    ) -> HttpResponse: ...


# ---------------------------------------------------------------------------
# Built-in stdlib transport (zero dependencies)
# ---------------------------------------------------------------------------


class UrllibTransport:
    """Default sync transport backed by :mod:`urllib.request`.

    Always available — requires no third-party dependencies. Suitable for
    scripts, CLIs and frameworks that do not bundle their own HTTP client.
    """

    def __init__(self, *, timeout: float | None = 30.0) -> None:
        self._timeout = timeout

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        content: Optional[bytes],
    ) -> HttpResponse:
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen

        req = Request(url, data=content, headers=dict(headers), method=method.upper())
        try:
            with urlopen(req, timeout=self._timeout) as resp:  # noqa: S310
                body = resp.read()
                return HttpResponse(
                    status_code=resp.status,
                    headers=dict(resp.headers.items()),
                    content=body,
                    reason=resp.reason or "",
                )
        except HTTPError as exc:
            body = exc.read() if exc.fp is not None else b""
            return HttpResponse(
                status_code=exc.code,
                headers=dict(exc.headers.items()) if exc.headers else {},
                content=body,
                reason=exc.reason or "",
            )


# ---------------------------------------------------------------------------
# Optional adapters — only constructed when the underlying lib is available
# ---------------------------------------------------------------------------


class HttpxTransport:
    """Wrap an :class:`httpx.Client` instance."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        content: Optional[bytes],
    ) -> HttpResponse:
        resp = self._client.request(
            method, url, headers=dict(headers), content=content
        )
        return HttpResponse(
            status_code=resp.status_code,
            headers=dict(resp.headers),
            content=resp.content,
            reason=getattr(resp, "reason_phrase", "") or "",
        )


class HttpxAsyncTransport:
    """Wrap an :class:`httpx.AsyncClient` instance."""

    def __init__(self, client: Any) -> None:
        self._client = client

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        content: Optional[bytes],
    ) -> HttpResponse:
        resp = await self._client.request(
            method, url, headers=dict(headers), content=content
        )
        return HttpResponse(
            status_code=resp.status_code,
            headers=dict(resp.headers),
            content=resp.content,
            reason=getattr(resp, "reason_phrase", "") or "",
        )


class RequestsTransport:
    """Wrap a :class:`requests.Session` instance."""

    def __init__(self, session: Any) -> None:
        self._session = session

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        content: Optional[bytes],
    ) -> HttpResponse:
        resp = self._session.request(
            method, url, headers=dict(headers), data=content
        )
        return HttpResponse(
            status_code=resp.status_code,
            headers=dict(resp.headers),
            content=resp.content,
            reason=getattr(resp, "reason", "") or "",
        )


class AiohttpTransport:
    """Wrap an :class:`aiohttp.ClientSession` instance."""

    def __init__(self, session: Any) -> None:
        self._session = session

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        content: Optional[bytes],
    ) -> HttpResponse:
        async with self._session.request(
            method, url, headers=dict(headers), data=content
        ) as resp:
            body = await resp.read()
            return HttpResponse(
                status_code=resp.status,
                headers=dict(resp.headers),
                content=body,
                reason=getattr(resp, "reason", "") or "",
            )


# ---------------------------------------------------------------------------
# Auto-detection helpers
# ---------------------------------------------------------------------------


def _module_class(obj: Any) -> str:
    cls = type(obj)
    return f"{cls.__module__}.{cls.__qualname__}"


def adapt_sync_transport(obj: Any) -> HttpTransport:
    """Return a sync :class:`HttpTransport` for *obj*.

    ``obj`` may be:
      * ``None`` — falls back to :class:`UrllibTransport`
      * a custom :class:`HttpTransport`
      * an ``httpx.Client``
      * a ``requests.Session``
    """

    if obj is None:
        return UrllibTransport()

    qualified = _module_class(obj)
    if qualified.startswith("httpx.") and "AsyncClient" not in qualified:
        return HttpxTransport(obj)
    if qualified.startswith("requests."):
        return RequestsTransport(obj)
    if isinstance(obj, HttpTransport):  # custom user transport
        return obj
    raise TypeError(
        f"Unsupported HTTP client {qualified!r}. Pass an httpx.Client, "
        "requests.Session, or an object implementing HttpTransport."
    )


def adapt_async_transport(obj: Any) -> AsyncHttpTransport:
    """Return an async :class:`AsyncHttpTransport` for *obj*.

    ``obj`` may be:
      * ``None`` — tries ``httpx.AsyncClient`` if installed, else raises
      * a custom :class:`AsyncHttpTransport`
      * an ``httpx.AsyncClient``
      * an ``aiohttp.ClientSession``
    """

    if obj is None:
        try:
            import httpx  # noqa: PLC0415
        except ImportError as exc:  # pragma: no cover - exercised when httpx absent
            raise RuntimeError(
                "AsyncKiriminAja requires either httpx or a custom "
                "async_http_client (e.g. an aiohttp.ClientSession). "
                "Install httpx with `pip install httpx`."
            ) from exc
        return HttpxAsyncTransport(httpx.AsyncClient())

    qualified = _module_class(obj)
    if "AsyncClient" in qualified and qualified.startswith("httpx."):
        return HttpxAsyncTransport(obj)
    if qualified.startswith("aiohttp."):
        return AiohttpTransport(obj)
    if isinstance(obj, AsyncHttpTransport):
        return obj
    raise TypeError(
        f"Unsupported async HTTP client {qualified!r}. Pass an "
        "httpx.AsyncClient, aiohttp.ClientSession, or an object "
        "implementing AsyncHttpTransport."
    )


__all__ = [
    "AiohttpTransport",
    "AsyncHttpTransport",
    "HttpResponse",
    "HttpTransport",
    "HttpxAsyncTransport",
    "HttpxTransport",
    "RequestsTransport",
    "UrllibTransport",
    "adapt_async_transport",
    "adapt_sync_transport",
]
