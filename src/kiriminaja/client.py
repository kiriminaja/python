from __future__ import annotations

from typing import Any

from .config import Config, Env
from .http import AsyncHttpClient, HttpClient
from .services.address import AddressService, AsyncAddressService
from .services.courier import AsyncCourierService, CourierService
from .services.coverage_area import AsyncCoverageAreaService, CoverageAreaService
from .services.order import AsyncOrderService, OrderService
from .services.payment import AsyncPaymentService, PaymentService
from .services.pickup import AsyncPickupService, PickupService


class KiriminAja:
    """Synchronous KiriminAja SDK client."""

    def __init__(
        self,
        *,
        env: Env = Env.SANDBOX,
        api_key: str = "",
        base_url: str = "",
        http_client: Any = None,
    ) -> None:
        self._config = Config(
            env=env,
            api_key=api_key,
            base_url=base_url,
            http_client=http_client,
        )
        self._http = HttpClient(self._config)

        self.address = AddressService(self._http)
        self.courier = CourierService(self._http)
        self.coverage_area = CoverageAreaService(self._http)
        self.order = OrderService(self._http)
        self.payment = PaymentService(self._http)
        self.pickup = PickupService(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> KiriminAja:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncKiriminAja:
    """Asynchronous KiriminAja SDK client."""

    def __init__(
        self,
        *,
        env: Env = Env.SANDBOX,
        api_key: str = "",
        base_url: str = "",
        async_http_client: Any = None,
    ) -> None:
        self._config = Config(
            env=env,
            api_key=api_key,
            base_url=base_url,
            async_http_client=async_http_client,
        )
        self._http = AsyncHttpClient(self._config)

        self.address = AsyncAddressService(self._http)
        self.courier = AsyncCourierService(self._http)
        self.coverage_area = AsyncCoverageAreaService(self._http)
        self.order = AsyncOrderService(self._http)
        self.payment = AsyncPaymentService(self._http)
        self.pickup = AsyncPickupService(self._http)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncKiriminAja:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
