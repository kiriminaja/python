from __future__ import annotations

from typing import Any

from ..http import AsyncHttpClient, HttpClient
from .normalization import normalize_balance


class CreditService:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def balance(self) -> Any:
        return self._client.get_json("/api/mitra/v6.2/credit/balance")

    def amount(self) -> float | int:
        return normalize_balance(self.balance())


class AsyncCreditService:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def balance(self) -> Any:
        return await self._client.get_json("/api/mitra/v6.2/credit/balance")

    async def amount(self) -> float | int:
        return normalize_balance(await self.balance())
