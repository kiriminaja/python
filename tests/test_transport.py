"""Verify the framework-agnostic transport layer."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import pytest

from kiriminaja import (
    AsyncHttpTransport,
    AsyncKiriminAja,
    HttpResponse,
    HttpTransport,
    KiriminAja,
    UrllibTransport,
)
from kiriminaja.transport import (
    AiohttpTransport,
    HttpxAsyncTransport,
    HttpxTransport,
    RequestsTransport,
    adapt_async_transport,
    adapt_sync_transport,
)


# ---------------------------------------------------------------------------
# Custom transports — exercise the public protocol contract
# ---------------------------------------------------------------------------


class _CustomSyncTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Mapping[str, str], Optional[bytes]]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        content: Optional[bytes],
    ) -> HttpResponse:
        self.calls.append((method, url, headers, content))
        return HttpResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            content=b'{"status": true}',
        )


class _CustomAsyncTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Mapping[str, str], Optional[bytes]]] = []

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        content: Optional[bytes],
    ) -> HttpResponse:
        self.calls.append((method, url, headers, content))
        return HttpResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            content=b'{"status": true}',
        )


class TestProtocolConformance:
    def test_custom_sync_transport_is_recognised(self) -> None:
        transport = _CustomSyncTransport()
        assert isinstance(transport, HttpTransport)
        assert adapt_sync_transport(transport) is transport

    def test_custom_async_transport_is_recognised(self) -> None:
        transport = _CustomAsyncTransport()
        assert isinstance(transport, AsyncHttpTransport)
        assert adapt_async_transport(transport) is transport

    def test_default_sync_falls_back_to_urllib(self) -> None:
        adapted = adapt_sync_transport(None)
        assert isinstance(adapted, UrllibTransport)


class TestSyncClientWithCustomTransport:
    def test_uses_custom_transport(self) -> None:
        transport = _CustomSyncTransport()
        client = KiriminAja(api_key="test", http_client=transport)
        client.address.provinces()
        assert len(transport.calls) == 1
        method, url, headers, _ = transport.calls[0]
        assert method == "POST"
        assert "/api/mitra/province" in url
        assert headers["Authorization"] == "Bearer test"


@pytest.mark.asyncio
class TestAsyncClientWithCustomTransport:
    async def test_uses_custom_transport(self) -> None:
        transport = _CustomAsyncTransport()
        client = AsyncKiriminAja(api_key="test", async_http_client=transport)
        await client.address.provinces()
        assert len(transport.calls) == 1
        method, url, _, _ = transport.calls[0]
        assert method == "POST"
        assert "/api/mitra/province" in url


# ---------------------------------------------------------------------------
# Auto-adaptation for httpx / requests / aiohttp
# ---------------------------------------------------------------------------


class TestAutoAdaptation:
    def test_httpx_client_is_wrapped(self) -> None:
        httpx = pytest.importorskip("httpx")

        client = httpx.Client()
        try:
            adapted = adapt_sync_transport(client)
            assert isinstance(adapted, HttpxTransport)
        finally:
            client.close()

    def test_httpx_async_client_is_wrapped(self) -> None:
        httpx = pytest.importorskip("httpx")

        client = httpx.AsyncClient()
        adapted = adapt_async_transport(client)
        assert isinstance(adapted, HttpxAsyncTransport)

    def test_requests_session_is_wrapped(self) -> None:
        requests = pytest.importorskip("requests")

        session = requests.Session()
        try:
            adapted = adapt_sync_transport(session)
            assert isinstance(adapted, RequestsTransport)
        finally:
            session.close()

    def test_aiohttp_session_is_wrapped(self) -> None:
        aiohttp = pytest.importorskip("aiohttp")

        async def _build() -> Any:
            session = aiohttp.ClientSession()
            try:
                return adapt_async_transport(session)
            finally:
                await session.close()

        import asyncio

        adapted = asyncio.run(_build())
        assert isinstance(adapted, AiohttpTransport)

    def test_unknown_sync_object_raises(self) -> None:
        class Bogus:
            pass

        with pytest.raises(TypeError):
            adapt_sync_transport(Bogus())

    def test_unknown_async_object_raises(self) -> None:
        class Bogus:
            pass

        with pytest.raises(TypeError):
            adapt_async_transport(Bogus())
