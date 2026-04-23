"""Volumetric calculator for multi-item packages."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Union


@dataclass(frozen=True)
class VolumetricItem:
    qty: int = 1
    length: float = 0
    width: float = 0
    height: float = 0


@dataclass(frozen=True)
class Dimensions:
    length: float = 0
    width: float = 0
    height: float = 0


ItemLike = Union[VolumetricItem, Mapping[str, float]]


def _coerce(item: ItemLike) -> VolumetricItem:
    if isinstance(item, VolumetricItem):
        return item
    return VolumetricItem(
        qty=int(item.get("qty", 1) or 1),
        length=item.get("length", 0) or 0,
        width=item.get("width", 0) or 0,
        height=item.get("height", 0) or 0,
    )


def calculate(items: Iterable[ItemLike]) -> Dimensions:
    """Return the smallest bounding box across vertical/horizontal/side stacking."""
    items = list(items)
    if not items:
        return Dimensions()

    l_vert = w_vert = h_vert = 0
    l_hor = w_hor = h_hor = 0
    l_side = w_side = h_side = 0

    for raw in items:
        it = _coerce(raw)
        qty = it.qty if it.qty >= 1 else 1
        l, w, h = it.length, it.width, it.height

        h_vert += h * qty
        if l > l_vert: l_vert = l
        if w > w_vert: w_vert = w

        l_hor += l * qty
        if h > h_hor: h_hor = h
        if w > w_hor: w_hor = w

        w_side += w * qty
        if h > h_side: h_side = h
        if l > l_side: l_side = l

    vol_vert = l_vert * w_vert * h_vert
    vol_hor = l_hor * w_hor * h_hor
    vol_side = l_side * w_side * h_side

    if vol_vert <= vol_hor and vol_vert <= vol_side:
        return Dimensions(length=l_vert, width=w_vert, height=h_vert)
    if vol_hor <= vol_side:
        return Dimensions(length=l_hor, width=w_hor, height=h_hor)
    return Dimensions(length=l_side, width=w_side, height=h_side)
