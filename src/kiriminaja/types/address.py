from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _clean(d: dict[str, Any]) -> dict[str, Any]:
    """Remove keys whose value is None (mirrors Go's omitempty)."""
    return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class PricingExpressPayload:
    origin: int
    destination: int
    weight: int
    item_value: int | str
    insurance: int
    courier: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "origin": self.origin,
            "destination": self.destination,
            "weight": self.weight,
            "item_value": self.item_value,
            "insurance": self.insurance,
            "courier": self.courier,
        }


@dataclass(slots=True)
class PricingInstantLocationPayload:
    lat: float
    long: float
    address: str

    def to_dict(self) -> dict[str, Any]:
        return {"lat": self.lat, "long": self.long, "address": self.address}


@dataclass(slots=True)
class PricingInstantPayload:
    service: list[str]
    item_price: float
    origin: PricingInstantLocationPayload
    destination: PricingInstantLocationPayload
    weight: int
    vehicle: str
    timezone: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": list(self.service),
            "item_price": self.item_price,
            "origin": self.origin.to_dict(),
            "destination": self.destination.to_dict(),
            "weight": self.weight,
            "vehicle": str(self.vehicle),
            "timezone": self.timezone,
        }
