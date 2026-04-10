from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


class InstantService(StrEnum):
    GRAB_EXPRESS = "grab_express"
    BORZO = "borzo"
    GOSEND = "gosend"


class InstantVehicle(StrEnum):
    BIKE = "motor"
    CAR = "mobil"
