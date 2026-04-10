from __future__ import annotations

from typing import Any

from ..http import AsyncHttpClient, HttpClient
from ..types.address import PricingExpressPayload, PricingInstantPayload
from .address import AddressService, AsyncAddressService


class CoverageAreaService(AddressService):
    def pricing_express(self, payload: PricingExpressPayload) -> Any:
        return self._client.post_json(
            "/api/mitra/v6.1/shipping_price", payload.to_dict()
        )

    def pricing_instant(self, payload: PricingInstantPayload) -> Any:
        return self._client.post_json(
            "/api/mitra/v4/instant/pricing", payload.to_dict()
        )


class AsyncCoverageAreaService(AsyncAddressService):
    async def pricing_express(self, payload: PricingExpressPayload) -> Any:
        return await self._client.post_json(
            "/api/mitra/v6.1/shipping_price", payload.to_dict()
        )

    async def pricing_instant(self, payload: PricingInstantPayload) -> Any:
        return await self._client.post_json(
            "/api/mitra/v4/instant/pricing", payload.to_dict()
        )
