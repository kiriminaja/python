from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _record(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _envelope_value(payload: Any, key: str) -> Any:
    root = _record(payload)
    if root is None:
        return None
    for envelope in ("results", "result", "data", "payload"):
        candidate = _record(root.get(envelope))
        if candidate is not None and key in candidate:
            return candidate[key]
    return root.get(key)


def normalize_profile(payload: Any) -> dict[str, Any]:
    root = _record(payload)
    if root is None:
        raise ValueError("profile response must be a JSON object")
    if root.get("status") is False:
        raise ValueError(str(root.get("message") or root.get("text") or "Profile request failed"))

    profile: Mapping[str, Any] | None = None
    for envelope in ("results", "result", "data"):
        candidate = _record(root.get(envelope))
        if candidate is not None:
            profile = candidate
            break
    if profile is None and any(key in root for key in ("id", "name", "email", "metadata")):
        profile = root
    if profile is None:
        raise ValueError("profile response does not contain profile data")

    return dict(profile)


def normalize_balance(payload: Any) -> float | int:
    root = _record(payload)
    if root is None:
        raise ValueError("credit response must be a JSON object")
    if root.get("status") is False:
        raise ValueError(str(root.get("message") or root.get("text") or "Credit request failed"))

    value = _envelope_value(payload, "balance")
    if isinstance(value, bool) or value is None:
        raise ValueError("credit response does not contain a numeric balance")
    try:
        balance = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("credit response does not contain a numeric balance") from exc
    if balance != balance or balance in (float("inf"), float("-inf")):
        raise ValueError("credit response does not contain a finite balance")
    return int(balance) if balance.is_integer() else balance
