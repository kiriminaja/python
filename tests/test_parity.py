from __future__ import annotations

import pytest

from kiriminaja import (
    AsyncKiriminAja,
    HttpResponse,
    KiriminAja,
    PricingExpressFullPayload,
    UrllibAsyncTransport,
)


class _Transport:
    def __init__(self, payload: object) -> None:
        self.payload = payload
        self.calls: list[tuple[str, str, bytes | None]] = []

    def request(self, method: str, url: str, *, headers, content):
        self.calls.append((method, url, content))
        import json

        return HttpResponse(200, {}, json.dumps(self.payload).encode())


class _AsyncTransport:
    def __init__(self, payload: object) -> None:
        self.payload = payload
        self.calls: list[tuple[str, str, bytes | None]] = []

    async def request(self, method: str, url: str, *, headers, content):
        self.calls.append((method, url, content))
        import json

        return HttpResponse(200, {}, json.dumps(self.payload).encode())


def test_async_default_transport_is_stdlib() -> None:
    from kiriminaja.transport import adapt_async_transport

    assert isinstance(adapt_async_transport(None), UrllibAsyncTransport)


def test_callback_and_full_pricing() -> None:
    transport = _Transport({"status": True})
    client = KiriminAja(api_key="key", http_client=transport)

    client.preference.set_callback("https://example.test/callback")
    client.coverage_area.pricing_express_full(
        PricingExpressFullPayload(origin=1, destination=2, weight=1000)
    )

    assert "/api/mitra/set_callback" in transport.calls[0][1]
    assert b'"url": "https://example.test/callback"' in transport.calls[0][2]
    assert "/api/mitra/v6.1/shipping_price" in transport.calls[1][1]
    assert b'"origin": 1' in transport.calls[1][2]


def test_profile_normalization_accepts_php_envelopes() -> None:
    for envelope in ("results", "result", "data"):
        transport = _Transport({envelope: {"id": 7, "name": "Shop"}})
        client = KiriminAja(http_client=transport)
        assert client.profile.normalized() == {"id": 7, "name": "Shop"}

    client = KiriminAja(http_client=_Transport({"id": 7, "name": "Shop"}))
    assert client.profile.normalized()["id"] == 7


def test_credit_normalization_accepts_php_envelopes_and_strings() -> None:
    for envelope in ("results", "result", "data", "payload"):
        transport = _Transport({envelope: {"balance": "12.50"}})
        client = KiriminAja(http_client=transport)
        assert client.credit.amount() == 12.5

    client = KiriminAja(http_client=_Transport({"balance": 0}))
    assert client.credit.amount() == 0


def test_normalization_rejects_missing_data_and_api_failure() -> None:
    with pytest.raises(ValueError, match="profile"):
        KiriminAja(http_client=_Transport({"status": True})).profile.normalized()
    with pytest.raises(ValueError, match="numeric balance"):
        KiriminAja(http_client=_Transport({"status": True})).credit.amount()
    with pytest.raises(ValueError, match="failed"):
        KiriminAja(http_client=_Transport({"status": False})).profile.normalized()


def test_preference_validation() -> None:
    client = KiriminAja(http_client=_Transport({"status": True}))
    with pytest.raises(ValueError):
        client.preference.set_callback("not-a-url")


@pytest.mark.asyncio
async def test_async_parity_methods() -> None:
    transport = _AsyncTransport({"results": {"balance": "4"}})
    client = AsyncKiriminAja(async_http_client=transport)
    assert await client.credit.amount() == 4
    await client.preference.set_callback("https://example.test/callback")
    assert "/api/mitra/set_callback" in transport.calls[1][1]
