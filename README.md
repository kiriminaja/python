# KiriminAja Python SDK

[![PyPI version](https://img.shields.io/pypi/v/kiriminaja)](https://pypi.org/project/kiriminaja/)
[![PyPI downloads](https://img.shields.io/pypi/dw/kiriminaja)](https://pypi.org/project/kiriminaja/)
[![license](https://img.shields.io/github/license/kiriminaja/python)](LICENSE)

Official Python SDK for the [KiriminAja](https://kiriminaja.com) logistics API. Supports both sync and async, and is **fully framework-agnostic** — works out of the box with the stdlib, or plug in your existing [httpx](https://www.python-httpx.org/), [requests](https://requests.readthedocs.io/), or [aiohttp](https://docs.aiohttp.org/) client.

## Requirements

- Python 3.10+
- No required runtime dependencies. Install an HTTP client only if you want one (`pip install kiriminaja[httpx]`, `[requests]`, or `[aiohttp]`).

## Installation

```bash
pip install kiriminaja
# Optional extras:
pip install "kiriminaja[httpx]"      # for httpx (sync + async)
pip install "kiriminaja[requests]"   # for requests (sync only)
pip install "kiriminaja[aiohttp]"    # for aiohttp (async only)
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

| Option        | Type  | Default          | Description                         |
| ------------- | ----- | ---------------- | ----------------------------------- |
| `env`         | `Env` | `Env.SANDBOX`    | Target environment                  |
| `api_key`     | `str` | —                | Your KiriminAja API key             |
| `base_url`    | `str` | Derived from env | Override the base URL               |
| `http_client` | `Any` | stdlib `urllib`  | Custom sync HTTP client (see below) |

For `AsyncKiriminAja`, use `async_http_client` instead. It defaults to `httpx.AsyncClient` when `httpx` is installed; otherwise pass an `aiohttp.ClientSession` or your own `AsyncHttpTransport`.

```python
# Custom base URL
client = KiriminAja(
    base_url="https://tdev.kiriminaja.com",
    api_key="YOUR_API_KEY",
)

# Plug in httpx
import httpx
client = KiriminAja(api_key="...", http_client=httpx.Client(timeout=10))

# Plug in requests
import requests
client = KiriminAja(api_key="...", http_client=requests.Session())

# Async with aiohttp
import aiohttp
async with aiohttp.ClientSession() as session:
    client = AsyncKiriminAja(api_key="...", async_http_client=session)
    await client.address.provinces()
```

### Bring your own transport

For frameworks that ship their own HTTP layer (e.g. internal proxies,
service meshes, sandboxed environments), implement `HttpTransport` /
`AsyncHttpTransport` directly:

```python
from kiriminaja import KiriminAja, HttpResponse, HttpTransport

class MyTransport(HttpTransport):
    def request(self, method, url, *, headers, content):
        # …call your own HTTP layer here…
        return HttpResponse(status_code=200, headers={}, content=b'{"status": true}')

client = KiriminAja(api_key="...", http_client=MyTransport())
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
from kiriminaja import (
    RequestPickupItem,
    RequestPickupItemMetadata,
    RequestPickupPackage,
    RequestPickupPayload,
)

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
            # `items` is optional. When provided, it lists the individual
            # items inside the package. `item_value` is still required.
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

### Credit

```python
# Get the current KiriminAja credit balance
client.credit.balance()
```

---

### Utilities — Volumetric

Estimate the smallest bounding box (length / width / height) for a
multi-item package by trying three stacking strategies and returning the
arrangement with the smallest volume.

```python
from kiriminaja.utils.volumetric import VolumetricItem, calculate

dim = calculate([
    VolumetricItem(qty=2, length=10, width=10, height=2),
    VolumetricItem(qty=1, length=5,  width=5,  height=5),
])
# dim.length, dim.width, dim.height
# Plain dicts are also accepted: {"qty": 2, "length": 10, ...}
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
