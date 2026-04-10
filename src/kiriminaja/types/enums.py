from __future__ import annotations

from enum import StrEnum


class InstantService(StrEnum):
    GRAB_EXPRESS = "grab_express"
    BORZO = "borzo"
    GOSEND = "gosend"


class InstantVehicle(StrEnum):
    BIKE = "motor"
    CAR = "mobil"
