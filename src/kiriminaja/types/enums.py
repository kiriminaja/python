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


class ExpressService(StrEnum):
    TIKI = "tiki"
    POS = "posindonesia"
    PAXEL = "paxel"
    NINJA = "ninja"
    RPX = "rpx"
    LION_PARCEL = "lion"
    JT_CARGO = "jtcargo"
    SENTRAL_CARGO = "sentral"
    ANTER_AJA = "anteraja"
    NCS = "ncs"
    SICEPAT = "sicepat"
    SAP = "sap"
    ID_EXPRESS = "idx"
    JNE = "jne"
    JNT = "jnt"
    SPX = "spx"
