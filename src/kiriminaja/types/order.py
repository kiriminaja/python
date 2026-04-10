from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .address import _clean


@dataclass(slots=True)
class RequestPickupPackage:
    order_id: str
    destination_name: str
    destination_phone: str
    destination_address: str
    destination_kecamatan_id: int
    weight: int
    width: int
    length: int
    height: int
    item_value: int
    shipping_cost: int
    service: str
    service_type: str
    cod: int
    package_type_id: int
    item_name: str
    destination_kelurahan_id: int | None = None
    destination_zipcode: str | None = None
    qty: int | None = None
    insurance_amount: float | None = None
    drop: bool | None = None
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "order_id": self.order_id,
            "destination_name": self.destination_name,
            "destination_phone": self.destination_phone,
            "destination_address": self.destination_address,
            "destination_kecamatan_id": self.destination_kecamatan_id,
            "weight": self.weight,
            "width": self.width,
            "length": self.length,
            "height": self.height,
            "item_value": self.item_value,
            "shipping_cost": self.shipping_cost,
            "service": self.service,
            "service_type": self.service_type,
            "cod": self.cod,
            "package_type_id": self.package_type_id,
            "item_name": self.item_name,
        }
        optional = {
            "destination_kelurahan_id": self.destination_kelurahan_id,
            "destination_zipcode": self.destination_zipcode,
            "qty": self.qty,
            "insurance_amount": self.insurance_amount,
            "drop": self.drop,
            "note": self.note,
        }
        d.update(_clean(optional))
        return d


@dataclass(slots=True)
class RequestPickupPayload:
    address: str
    phone: str
    name: str
    kecamatan_id: int
    packages: list[RequestPickupPackage]
    schedule: str
    zipcode: str | None = None
    kelurahan_id: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    platform_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "address": self.address,
            "phone": self.phone,
            "name": self.name,
            "kecamatan_id": self.kecamatan_id,
            "packages": [p.to_dict() for p in self.packages],
            "schedule": self.schedule,
        }
        optional = {
            "zipcode": self.zipcode,
            "kelurahan_id": self.kelurahan_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "platform_name": self.platform_name,
        }
        d.update(_clean(optional))
        return d


@dataclass(slots=True)
class InstantPickupItem:
    name: str
    description: str
    price: int
    weight: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "weight": self.weight,
        }


@dataclass(slots=True)
class InstantPickupPackage:
    origin_name: str
    origin_phone: str
    origin_lat: float
    origin_long: float
    origin_address: str
    origin_address_note: str
    destination_name: str
    destination_phone: str
    destination_lat: float
    destination_long: float
    destination_address: str
    destination_address_note: str
    shipping_price: int
    item: InstantPickupItem

    def to_dict(self) -> dict[str, Any]:
        return {
            "origin_name": self.origin_name,
            "origin_phone": self.origin_phone,
            "origin_lat": self.origin_lat,
            "origin_long": self.origin_long,
            "origin_address": self.origin_address,
            "origin_address_note": self.origin_address_note,
            "destination_name": self.destination_name,
            "destination_phone": self.destination_phone,
            "destination_lat": self.destination_lat,
            "destination_long": self.destination_long,
            "destination_address": self.destination_address,
            "destination_address_note": self.destination_address_note,
            "shipping_price": self.shipping_price,
            "item": self.item.to_dict(),
        }


@dataclass(slots=True)
class InstantPickupPayload:
    service: str
    service_type: str
    vehicle: str
    order_prefix: str
    packages: list[InstantPickupPackage]

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": str(self.service),
            "service_type": self.service_type,
            "vehicle": str(self.vehicle),
            "order_prefix": self.order_prefix,
            "packages": [p.to_dict() for p in self.packages],
        }
