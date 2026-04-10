"""Async client tests — mirrors sync test suite."""

from __future__ import annotations

import json

import httpx
import pytest

from kiriminaja import AsyncKiriminAja, Env, InstantService, InstantVehicle
from kiriminaja.types.address import (
    PricingExpressPayload,
    PricingInstantLocationPayload,
    PricingInstantPayload,
)
from kiriminaja.types.order import (
    InstantPickupItem,
    InstantPickupPackage,
    InstantPickupPayload,
    RequestPickupPackage,
    RequestPickupPayload,
)


class _AsyncRecordingTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.calls: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.calls = [*self.calls, request]
        return httpx.Response(200, json={"status": True})


def _make_async_client(
    env: Env = Env.SANDBOX,
    api_key: str = "test-key",
) -> tuple[AsyncKiriminAja, _AsyncRecordingTransport]:
    transport = _AsyncRecordingTransport()
    http_client = httpx.AsyncClient(transport=transport)
    client = AsyncKiriminAja(env=env, api_key=api_key, async_http_client=http_client)
    return client, transport


@pytest.mark.asyncio
class TestAsyncConfig:
    async def test_sandbox_base_url(self) -> None:
        client, transport = _make_async_client(env=Env.SANDBOX)
        await client.address.provinces()
        assert "tdev.kiriminaja.com" in str(transport.calls[0].url)

    async def test_production_base_url(self) -> None:
        client, transport = _make_async_client(env=Env.PRODUCTION)
        await client.address.provinces()
        assert "client.kiriminaja.com" in str(transport.calls[0].url)

    async def test_bearer_token(self) -> None:
        client, transport = _make_async_client(api_key="ASYNC_KEY")
        await client.address.provinces()
        assert transport.calls[0].headers["authorization"] == "Bearer ASYNC_KEY"


@pytest.mark.asyncio
class TestAsyncAddress:
    async def test_provinces(self) -> None:
        client, transport = _make_async_client()
        await client.address.provinces()
        assert "/api/mitra/province" in str(transport.calls[0].url)
        assert transport.calls[0].method == "POST"

    async def test_cities(self) -> None:
        client, transport = _make_async_client()
        await client.address.cities(5)
        body = json.loads(transport.calls[0].content)
        assert body == {"provinsi_id": 5}

    async def test_districts_by_name(self) -> None:
        client, transport = _make_async_client()
        await client.address.districts_by_name("jakarta")
        body = json.loads(transport.calls[0].content)
        assert body == {"search": "jakarta"}


@pytest.mark.asyncio
class TestAsyncCoverageArea:
    async def test_pricing_express(self) -> None:
        client, transport = _make_async_client()
        payload = PricingExpressPayload(
            origin=1, destination=2, weight=1000,
            item_value=50000, insurance=0, courier=["jne"],
        )
        await client.coverage_area.pricing_express(payload)
        assert "/api/mitra/v6.1/shipping_price" in str(transport.calls[0].url)

    async def test_pricing_instant(self) -> None:
        client, transport = _make_async_client()
        payload = PricingInstantPayload(
            service=[InstantService.GOSEND],
            item_price=10000,
            origin=PricingInstantLocationPayload(lat=-6.2, long=106.8, address="A"),
            destination=PricingInstantLocationPayload(lat=-6.21, long=106.81, address="B"),
            weight=1000,
            vehicle=InstantVehicle.BIKE,
            timezone="Asia/Jakarta",
        )
        await client.coverage_area.pricing_instant(payload)
        assert "/api/mitra/v4/instant/pricing" in str(transport.calls[0].url)


@pytest.mark.asyncio
class TestAsyncOrderExpress:
    async def test_track(self) -> None:
        client, transport = _make_async_client()
        await client.order.express.track("OID_EXP_1")
        assert "/api/mitra/tracking" in str(transport.calls[0].url)
        body = json.loads(transport.calls[0].content)
        assert body == {"order_id": "OID_EXP_1"}

    async def test_cancel(self) -> None:
        client, transport = _make_async_client()
        await client.order.express.cancel("AWB123", "reason here")
        url = str(transport.calls[0].url)
        assert "/api/mitra/v3/cancel_shipment" in url
        assert "awb=AWB123" in url

    async def test_request_pickup(self) -> None:
        client, transport = _make_async_client()
        payload = RequestPickupPayload(
            address="Jl. Jodipati No.29",
            phone="08133345678",
            name="Tokotries",
            kecamatan_id=548,
            schedule="2021-11-30 22:00:00",
            packages=[
                RequestPickupPackage(
                    order_id="YGL-000000019",
                    destination_name="Flag Test",
                    destination_phone="082223323333",
                    destination_address="Jl. Magelang KM 11",
                    destination_kecamatan_id=548,
                    weight=520, width=8, length=8, height=8,
                    item_value=275000, shipping_cost=65000,
                    service="jne", service_type="REG23",
                    cod=0, package_type_id=7,
                    item_name="TEST Item name",
                ),
            ],
        )
        await client.order.express.request_pickup(payload)
        assert "/api/mitra/v6.1/request_pickup" in str(transport.calls[0].url)
        body = json.loads(transport.calls[0].content)
        assert body == payload.to_dict()


@pytest.mark.asyncio
class TestAsyncOrderInstant:
    async def test_create(self) -> None:
        client, transport = _make_async_client()
        payload = InstantPickupPayload(
            service=InstantService.GOSEND,
            service_type="instant",
            vehicle=InstantVehicle.BIKE,
            order_prefix="BDI",
            packages=[
                InstantPickupPackage(
                    origin_name="Rizky",
                    origin_phone="081280045616",
                    origin_lat=-7.854584,
                    origin_long=110.331154,
                    origin_address="Wirobrajan, Yogyakarta",
                    origin_address_note="Dekat Kantor",
                    destination_name="Okka",
                    destination_phone="081280045616",
                    destination_lat=-7.776192,
                    destination_long=110.325053,
                    destination_address="Godean, Sleman",
                    destination_address_note="Dekat Pasar",
                    shipping_price=34000,
                    item=InstantPickupItem(
                        name="Barang 1",
                        description="Barang 1 Description",
                        price=20000,
                        weight=1000,
                    ),
                ),
            ],
        )
        await client.order.instant.create(payload)
        assert "/api/mitra/v4/instant/pickup/request" in str(transport.calls[0].url)

    async def test_track(self) -> None:
        client, transport = _make_async_client()
        await client.order.instant.track("OID123")
        assert "/api/mitra/v4/instant/tracking/OID123" in str(transport.calls[0].url)
        assert transport.calls[0].method == "GET"

    async def test_cancel(self) -> None:
        client, transport = _make_async_client()
        await client.order.instant.cancel("OID123")
        assert "/api/mitra/v4/instant/pickup/void/OID123" in str(transport.calls[0].url)
        assert transport.calls[0].method == "DELETE"

    async def test_find_new_driver(self) -> None:
        client, transport = _make_async_client()
        await client.order.instant.find_new_driver("OID123")
        body = json.loads(transport.calls[0].content)
        assert body == {"order_id": "OID123"}


@pytest.mark.asyncio
class TestAsyncCourier:
    async def test_list(self) -> None:
        client, transport = _make_async_client()
        await client.courier.list()
        assert "/api/mitra/couriers" in str(transport.calls[0].url)

    async def test_set_whitelist_services(self) -> None:
        client, transport = _make_async_client()
        await client.courier.set_whitelist_services(["jne_reg"])
        body = json.loads(transport.calls[0].content)
        assert body == {"services": ["jne_reg"]}


@pytest.mark.asyncio
class TestAsyncPickup:
    async def test_schedules(self) -> None:
        client, transport = _make_async_client()
        await client.pickup.schedules()
        assert "/api/mitra/v2/schedules" in str(transport.calls[0].url)


@pytest.mark.asyncio
class TestAsyncPayment:
    async def test_get_payment(self) -> None:
        client, transport = _make_async_client()
        await client.payment.get_payment("PAY123")
        body = json.loads(transport.calls[0].content)
        assert body == {"payment_id": "PAY123"}
