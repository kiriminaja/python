"""Sync client + services tests — mirrors Go/Node test patterns."""

from __future__ import annotations

import json

import httpx
import pytest

from kiriminaja import (
    Env,
    ExpressService,
    InstantPickupItem,
    InstantPickupPackage,
    InstantPickupPayload,
    InstantService,
    InstantVehicle,
    KiriminAja,
    PricingExpressPayload,
    PricingInstantLocationPayload,
    PricingInstantPayload,
    RequestPickupItem,
    RequestPickupItemMetadata,
    RequestPickupPackage,
    RequestPickupPayload,
)


# ---------------------------------------------------------------------------
# Mock transport — records every request
# ---------------------------------------------------------------------------

class _RecordingTransport(httpx.BaseTransport):
    def __init__(self) -> None:
        self.calls: list[httpx.Request] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.calls = [*self.calls, request]
        return httpx.Response(200, json={"status": True})


def _make_client(
    env: Env = Env.SANDBOX,
    api_key: str = "test-key",
) -> tuple[KiriminAja, _RecordingTransport]:
    transport = _RecordingTransport()
    http_client = httpx.Client(transport=transport)
    client = KiriminAja(env=env, api_key=api_key, http_client=http_client)
    return client, transport


# ---------------------------------------------------------------------------
# Config / env
# ---------------------------------------------------------------------------


class TestConfig:
    def test_sandbox_base_url(self) -> None:
        client, transport = _make_client(env=Env.SANDBOX)
        client.address.provinces()
        assert "tdev.kiriminaja.com" in str(transport.calls[0].url)

    def test_production_base_url(self) -> None:
        client, transport = _make_client(env=Env.PRODUCTION)
        client.address.provinces()
        assert "client.kiriminaja.com" in str(transport.calls[0].url)

    def test_bearer_token(self) -> None:
        client, transport = _make_client(api_key="MY_KEY")
        client.address.provinces()
        assert transport.calls[0].headers["authorization"] == "Bearer MY_KEY"


# ---------------------------------------------------------------------------
# Address service
# ---------------------------------------------------------------------------


class TestAddress:
    def test_provinces(self) -> None:
        client, transport = _make_client()
        client.address.provinces()
        assert "/api/mitra/province" in str(transport.calls[0].url)
        assert transport.calls[0].method == "POST"

    def test_cities(self) -> None:
        client, transport = _make_client()
        client.address.cities(5)
        assert "/api/mitra/city" in str(transport.calls[0].url)
        body = json.loads(transport.calls[0].content)
        assert body == {"provinsi_id": 5}

    def test_districts(self) -> None:
        client, transport = _make_client()
        client.address.districts(12)
        assert "/api/mitra/kecamatan" in str(transport.calls[0].url)
        body = json.loads(transport.calls[0].content)
        assert body == {"kabupaten_id": 12}

    def test_sub_districts(self) -> None:
        client, transport = _make_client()
        client.address.sub_districts(77)
        assert "/api/mitra/kelurahan" in str(transport.calls[0].url)
        body = json.loads(transport.calls[0].content)
        assert body == {"kecamatan_id": 77}

    def test_districts_by_name(self) -> None:
        client, transport = _make_client()
        client.address.districts_by_name("jakarta")
        assert "/api/mitra/v2/get_address_by_name" in str(transport.calls[0].url)
        body = json.loads(transport.calls[0].content)
        assert body == {"search": "jakarta"}


# ---------------------------------------------------------------------------
# Coverage area + pricing
# ---------------------------------------------------------------------------


class TestCoverageArea:
    def test_pricing_express(self) -> None:
        client, transport = _make_client()
        payload = PricingExpressPayload(
            origin=1,
            destination=2,
            weight=1000,
            item_value=50000,
            insurance=0,
            courier=[ExpressService.JNE, "other"],
        )
        client.coverage_area.pricing_express(payload)
        assert "/api/mitra/v6.1/shipping_price" in str(transport.calls[0].url)
        assert transport.calls[0].method == "POST"
        assert transport.calls[0].headers["content-type"] == "application/json"
        body = json.loads(transport.calls[0].content)
        assert body == payload.to_dict()

    def test_pricing_instant(self) -> None:
        client, transport = _make_client()
        payload = PricingInstantPayload(
            service=[InstantService.GOSEND, "other"],
            item_price=10000,
            origin=PricingInstantLocationPayload(lat=-6.2, long=106.8, address="A"),
            destination=PricingInstantLocationPayload(lat=-6.21, long=106.81, address="B"),
            weight=1000,
            vehicle=InstantVehicle.BIKE,
            timezone="Asia/Jakarta",
        )
        client.coverage_area.pricing_instant(payload)
        assert "/api/mitra/v4/instant/pricing" in str(transport.calls[0].url)
        body = json.loads(transport.calls[0].content)
        assert body == payload.to_dict()


# ---------------------------------------------------------------------------
# Order — Express
# ---------------------------------------------------------------------------


class TestOrderExpress:
    def test_track(self) -> None:
        client, transport = _make_client()
        client.order.express.track("OID_EXP_1")
        assert "/api/mitra/tracking" in str(transport.calls[0].url)
        assert transport.calls[0].method == "POST"
        body = json.loads(transport.calls[0].content)
        assert body == {"order_id": "OID_EXP_1"}

    def test_cancel(self) -> None:
        client, transport = _make_client()
        client.order.express.cancel("AWB123", "reason here")
        url = str(transport.calls[0].url)
        assert "/api/mitra/v3/cancel_shipment" in url
        assert "awb=AWB123" in url
        assert "reason=reason+here" in url
        assert transport.calls[0].method == "POST"

    def test_request_pickup(self) -> None:
        client, transport = _make_client()
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
                    weight=520,
                    width=8,
                    length=8,
                    height=8,
                    item_value=275000,
                    shipping_cost=65000,
                    service="jne",
                    service_type="REG23",
                    cod=0,
                    package_type_id=7,
                    item_name="TEST Item name",
                    items=[
                        RequestPickupItem(
                            name="Kaos Polos",
                            price=125000,
                            qty=2,
                            weight=260,
                            width=4,
                            length=4,
                            height=4,
                            metadata=RequestPickupItemMetadata(
                                sku="KP-001",
                                variant_label="Merah / L",
                            ),
                        ),
                    ],
                ),
            ],
        )
        client.order.express.request_pickup(payload)
        assert "/api/mitra/v6.1/request_pickup" in str(transport.calls[0].url)
        assert transport.calls[0].method == "POST"
        body = json.loads(transport.calls[0].content)
        assert body == payload.to_dict()


# ---------------------------------------------------------------------------
# Order — Instant
# ---------------------------------------------------------------------------


class TestOrderInstant:
    def _payload(self) -> InstantPickupPayload:
        return InstantPickupPayload(
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

    def test_create(self) -> None:
        client, transport = _make_client()
        payload = self._payload()
        client.order.instant.create(payload)
        assert "/api/mitra/v4/instant/pickup/request" in str(transport.calls[0].url)
        assert transport.calls[0].method == "POST"
        body = json.loads(transport.calls[0].content)
        assert body == payload.to_dict()

    def test_track(self) -> None:
        client, transport = _make_client()
        client.order.instant.track("OID123")
        assert "/api/mitra/v4/instant/tracking/OID123" in str(transport.calls[0].url)
        assert transport.calls[0].method == "GET"

    def test_cancel(self) -> None:
        client, transport = _make_client()
        client.order.instant.cancel("OID123")
        assert "/api/mitra/v4/instant/pickup/void/OID123" in str(transport.calls[0].url)
        assert transport.calls[0].method == "DELETE"

    def test_find_new_driver(self) -> None:
        client, transport = _make_client()
        client.order.instant.find_new_driver("OID123")
        assert "/api/mitra/v4/instant/pickup/find-new-driver" in str(
            transport.calls[0].url
        )
        body = json.loads(transport.calls[0].content)
        assert body == {"order_id": "OID123"}


# ---------------------------------------------------------------------------
# Courier
# ---------------------------------------------------------------------------


class TestCourier:
    def test_list(self) -> None:
        client, transport = _make_client()
        client.courier.list()
        assert "/api/mitra/couriers" in str(transport.calls[0].url)
        assert transport.calls[0].method == "POST"

    def test_group(self) -> None:
        client, transport = _make_client()
        client.courier.group()
        assert "/api/mitra/couriers_group" in str(transport.calls[0].url)

    def test_detail(self) -> None:
        client, transport = _make_client()
        client.courier.detail("jne")
        body = json.loads(transport.calls[0].content)
        assert body == {"courier_code": "jne"}

    def test_set_whitelist_services(self) -> None:
        client, transport = _make_client()
        client.courier.set_whitelist_services(["jne_reg", "jne_yes"])
        assert "/api/mitra/v3/set_whitelist_services" in str(transport.calls[0].url)
        body = json.loads(transport.calls[0].content)
        assert body == {"services": ["jne_reg", "jne_yes"]}


# ---------------------------------------------------------------------------
# Pickup
# ---------------------------------------------------------------------------


class TestPickup:
    def test_schedules(self) -> None:
        client, transport = _make_client()
        client.pickup.schedules()
        assert "/api/mitra/v2/schedules" in str(transport.calls[0].url)
        assert transport.calls[0].method == "POST"


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------


class TestPayment:
    def test_get_payment(self) -> None:
        client, transport = _make_client()
        client.payment.get_payment("PAY123")
        assert "/api/mitra/v2/get_payment" in str(transport.calls[0].url)
        body = json.loads(transport.calls[0].content)
        assert body == {"payment_id": "PAY123"}
