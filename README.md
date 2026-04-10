# KiriminAja Python SDK

[![PyPI version](https://img.shields.io/pypi/v/kiriminaja)](https://pypi.org/project/kiriminaja/)
[![PyPI downloads](https://img.shields.io/pypi/dw/kiriminaja)](https://pypi.org/project/kiriminaja/)
[![license](https://img.shields.io/github/license/kiriminaja/python)](LICENSE)

Official Python SDK for the [KiriminAja](https://kiriminaja.com) logistics API. Supports both sync and async via [httpx](https://www.python-httpx.org/).

## Requirements

- Python 3.10+

## Installation

```bash
pip install kiriminaja
# uv add kiriminaja
# poetry add kiriminaja
```

---

## Quick Start

Create a client with your API key, then call any service method.

```python
from kiriminaja import KiriminAja, Env

client = KiriminAja(
    env=Env.SANDBOX,  # or Env.PRODUCTION
    api_key="YOUR_API_KEY",
)

# Use any service
provinces = client.address.provinces()
```

### Async

```python
from kiriminaja import AsyncKiriminAja, Env

async with AsyncKiriminAja(env=Env.SANDBOX, api_key="YOUR_API_KEY") as client:
    provinces = await client.address.provinces()
```

---

## Config Options

| Option        | Type           | Default          | Description                          |
| ------------- | -------------- | ---------------- | ------------------------------------ |
| `env`         | `Env`          | `Env.SANDBOX`    | Target environment                   |
| `api_key`     | `str`          | —                | Your KiriminAja API key              |
| `base_url`    | `str`          | Derived from env | Override the base URL                |
| `http_client` | `httpx.Client` | auto-created     | Custom sync HTTP client (proxy/mock) |

For `AsyncKiriminAja`, use `async_http_client` (`httpx.AsyncClient`) instead.

```python
# Custom base URL
client = KiriminAja(
    base_url="https://tdev.kiriminaja.com",
    api_key="YOUR_API_KEY",
)

# Custom httpx client (e.g. with timeout or proxy)
import httpx

client = KiriminAja(
    api_key="...",
    http_client=httpx.Client(timeout=10),
)
```

---

## Services

### Address

```python
# List all provinces
client.address.provinces()

# Cities in a province (provinsi_id)
client.address.cities(5)

# Districts in a city (kabupaten_id)
client.address.districts(12)

# Sub-districts in a district (kecamatan_id)
client.address.sub_districts(77)

# Search districts by name
client.address.districts_by_name("jakarta")
```

---

### Coverage Area & Pricing

```python
from kiriminaja import (
    PricingExpressPayload,
    PricingInstantPayload,
    PricingInstantLocationPayload,
    InstantService,
    InstantVehicle,
)

# Express shipping rates
client.coverage_area.pricing_express(PricingExpressPayload(
    origin=1,
    destination=2,
    weight=1000,  # grams
    item_value=50000,
    insurance=0,
    courier=["jne", "jnt"],
))

# Instant (same-day) rates
client.coverage_area.pricing_instant(PricingInstantPayload(
    service=[InstantService.GOSEND],
    item_price=10000,
    origin=PricingInstantLocationPayload(lat=-6.2, long=106.8, address="Jl. Sudirman No.1"),
    destination=PricingInstantLocationPayload(lat=-6.21, long=106.81, address="Jl. Thamrin No.5"),
    weight=1000,
    vehicle=InstantVehicle.BIKE,
    timezone="Asia/Jakarta",
))
```

---

### Order — Express

```python
from kiriminaja import RequestPickupPayload, RequestPickupPackage

# Track by order ID
client.order.express.track("ORDER123")

# Cancel by AWB
client.order.express.cancel("AWB123456", "Customer request")

# Request pickup
client.order.express.request_pickup(RequestPickupPayload(
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
        ),
    ],
))
```

---

### Order — Instant

```python
from kiriminaja import (
    InstantPickupPayload,
    InstantPickupPackage,
    InstantPickupItem,
    InstantService,
    InstantVehicle,
)

# Create instant pickup
client.order.instant.create(InstantPickupPayload(
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
))

# Find a new driver for an existing order
client.order.instant.find_new_driver("ORDER123")

# Cancel instant order
client.order.instant.cancel("ORDER123")

# Track instant order
client.order.instant.track("ORDER123")
```

---

### Courier

```python
# List available couriers
client.courier.list()

# Courier groups
client.courier.group()

# Courier service detail
client.courier.detail("jne")

# Set whitelist services
client.courier.set_whitelist_services(["jne_reg", "jne_yes"])
```

---

### Pickup Schedules

```python
client.pickup.schedules()
```

---

### Payment

```python
client.payment.get_payment("PAY123")
```

---

## Contributing

For any requests, bugs, or comments, please open an [issue](https://github.com/kiriminaja/python/issues) or [submit a pull request](https://github.com/kiriminaja/python/pulls).

## Development

```bash
uv sync          # install dependencies
uv run pytest    # run tests
uv run mypy src/ # typecheck
```
