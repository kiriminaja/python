from __future__ import annotations

from typing import Any

from ..http import AsyncHttpClient, HttpClient


class PaymentService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_payment(self, payment_id: str) -> Any:
        return self._client.post_json(
            "/api/mitra/v2/get_payment", {"payment_id": payment_id}
        )


class AsyncPaymentService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def get_payment(self, payment_id: str) -> Any:
        return await self._client.post_json(
            "/api/mitra/v2/get_payment", {"payment_id": payment_id}
        )
