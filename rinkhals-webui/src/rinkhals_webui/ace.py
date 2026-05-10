from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Dict, List, Optional

from .klippy import KlippyClient, KlippyError


_CONFIG_KEYS = (
    "auto_refill",
    "runout_detect",
)

class ACEController:
    """Controller for interacting with the ACE filament hub."""

    def __init__(self, client: Optional[KlippyClient] = None) -> None:
        self._client = client or KlippyClient()

    def list_hubs(self) -> List[Dict[str, Any]]:
        response = self._client.call("objects/query", params={"objects": {"filament_hub": None}})
        try:
            hubs = response["result"]["status"]["filament_hub"]["filament_hubs"]
        except KeyError as e:
            raise KlippyError("Klippy returned an incomplete ACE status payload") from e

        if not isinstance(hubs, Iterable):
            raise KlippyError("Klippy returned an invalid ACE hub list")

        normalized: List[Dict[str, Any]] = []
        for hub in hubs:
            if not isinstance(hub, Mapping):
                continue
            normalized.append(_normalize_hub(hub))
        return normalized

    def fetch_config(self) -> Dict[str, Any]:
        response = self._client.call("filament_hub/get_config")
        result = response.get("result")
        if not isinstance(result, Mapping):
            raise KlippyError("Klippy returned an invalid ACE config")
        return {key: result.get(key) for key in _CONFIG_KEYS if key in result}

    def update_config(self, updates: Mapping[str, Any]) -> None:
        if not updates:
            raise ValueError("No configuration values supplied")

        payload = {key: updates[key] for key in _CONFIG_KEYS if key in updates}
        if not payload:
            raise ValueError("No supported configuration values supplied")

        self._client.call("filament_hub/set_config", params=payload)

    def set_filament(self, ace_id: int, slot: int, material: str, color_hex: str) -> None:
        payload = {
            "id": ace_id,
            "index": slot,
            "type": material,
            "color": _parse_color_hex(color_hex),
        }
        self._client.call("filament_hub/set_filament_info", params=payload)

    def start_drying(self, ace_id: int, duration: int, temp: int, fan_speed: Optional[int]) -> None:
        if duration <= 0:
            raise ValueError("Duration must be greater than zero")
        if temp <= 0:
            raise ValueError("Temperature must be greater than zero")
        if fan_speed is not None and fan_speed < 0:
            raise ValueError("Fan speed must be non-negative")

        payload = {
            "id": ace_id,
            "duration": duration,
            "temp": temp,
            "fan_speed": 0 if fan_speed is None else max(0, fan_speed),
        }
        self._client.call("filament_hub/start_drying", params=payload)

    def stop_drying(self, ace_id: int) -> None:
        self._client.call("filament_hub/stop_drying", params={"id": ace_id})


def _normalize_hub(hub: Mapping[str, Any]) -> Dict[str, Any]:
    slots = []
    for slot in hub.get("slots", []):
        slots.append(
            {
                "index": slot.get("index"),
                "status": slot.get("status"),
                "type": slot.get("type"),
                "color": _normalize_slot_color(slot.get("color")),
            }
        )

    dryer_status = hub.get("dryer_status") or {}
    dryer = {
        "status": dryer_status.get("status"),
        "target_temp": dryer_status.get("target_temp"),
        "remaining_seconds": dryer_status.get("remain_time"),
        "is_active": dryer_status.get("status") not in (None, "stop"),
    }

    return {
        "id": hub.get("id"),
        "status": hub.get("status"),
        "temperature": hub.get("temp"),
        "slots": slots,
        "dryer": dryer,
    }


def _normalize_slot_color(color: Any) -> Optional[Dict[str, Any]]:
    triplet = list(color)
    if len(triplet) != 3:
        return None
    try:
        r, g, b = (int(component) for component in triplet)
    except (TypeError, ValueError):
        return None
    return {"rgb": {"r": r, "g": g, "b": b}, "hex": f"#{r:02X}{g:02X}{b:02X}"}


def _parse_color_hex(color_hex: str) -> Dict[str, int]:
    value = color_hex.strip()
    if value.startswith("#"):
        value = value[1:]
    if len(value) != 6:
        raise ValueError("Color must use the #RRGGBB format")

    try:
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
    except ValueError as e:
        raise ValueError("Color must be a valid hex value") from e
    return {"R": r, "G": g, "B": b}

