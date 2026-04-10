from __future__ import annotations

from typing import Any

from ..http import AsyncHttpClient, HttpClient
from ..types.order import InstantPickupPayload, RequestPickupPayload


class ExpressOrderService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def track(self, order_id: str) -> Any:
        return self._client.post_json("/api/mitra/tracking", {"order_id": order_id})

    def cancel(self, awb: str, reason: str) -> Any:
        return self._client.request_json(
            "/api/mitra/v3/cancel_shipment",
            method="POST",
            query={"awb": awb, "reason": reason},
        )

    def request_pickup(self, payload: RequestPickupPayload) -> Any:
        return self._client.post_json(
            "/api/mitra/v6.1/request_pickup", payload.to_dict()
        )


class InstantOrderService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def create(self, payload: InstantPickupPayload) -> Any:
        return self._client.post_json(
            "/api/mitra/v4/instant/pickup/request", payload.to_dict()
        )

    def track(self, order_id: str) -> Any:
        return self._client.get_json(f"/api/mitra/v4/instant/tracking/{order_id}")

    def cancel(self, order_id: str) -> Any:
        return self._client.delete_json(
            f"/api/mitra/v4/instant/pickup/void/{order_id}"
        )

    def find_new_driver(self, order_id: str) -> Any:
        return self._client.post_json(
            "/api/mitra/v4/instant/pickup/find-new-driver",
            {"order_id": order_id},
        )


class OrderService:
    def __init__(self, client: HttpClient) -> None:
        self.express = ExpressOrderService(client)
        self.instant = InstantOrderService(client)


# -- Async variants -------------------------------------------------------


class AsyncExpressOrderService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def track(self, order_id: str) -> Any:
        return await self._client.post_json(
            "/api/mitra/tracking", {"order_id": order_id}
        )

    async def cancel(self, awb: str, reason: str) -> Any:
        return await self._client.request_json(
            "/api/mitra/v3/cancel_shipment",
            method="POST",
            query={"awb": awb, "reason": reason},
        )

    async def request_pickup(self, payload: RequestPickupPayload) -> Any:
        return await self._client.post_json(
            "/api/mitra/v6.1/request_pickup", payload.to_dict()
        )


class AsyncInstantOrderService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def create(self, payload: InstantPickupPayload) -> Any:
        return await self._client.post_json(
            "/api/mitra/v4/instant/pickup/request", payload.to_dict()
        )

    async def track(self, order_id: str) -> Any:
        return await self._client.get_json(
            f"/api/mitra/v4/instant/tracking/{order_id}"
        )

    async def cancel(self, order_id: str) -> Any:
        return await self._client.delete_json(
            f"/api/mitra/v4/instant/pickup/void/{order_id}"
        )

    async def find_new_driver(self, order_id: str) -> Any:
        return await self._client.post_json(
            "/api/mitra/v4/instant/pickup/find-new-driver",
            {"order_id": order_id},
        )


class AsyncOrderService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self.express = AsyncExpressOrderService(client)
        self.instant = AsyncInstantOrderService(client)
