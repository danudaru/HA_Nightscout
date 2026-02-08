"""Utility functions for Nightscout integration."""
from __future__ import annotations

from datetime import datetime

from .const import DIRECTION_ICONS


def format_timestamp(timestamp: int | str | None) -> str | None:
    """Format timestamp to ISO string."""
    if timestamp is None:
        return None

    try:
        if isinstance(timestamp, str):
            return timestamp

        # Convert milliseconds to seconds
        if timestamp > 10000000000:
            timestamp = timestamp / 1000

        dt = datetime.fromtimestamp(timestamp)
        return dt.isoformat()
    except (ValueError, OSError):
        return None


def get_direction_icon(direction: str | None) -> str:
    """Get icon for glucose direction."""
    if direction is None:
        return DIRECTION_ICONS.get("NONE", "⊝")
    return DIRECTION_ICONS.get(direction, "⊝")


def mgdl_to_mmol(mgdl: float) -> float:
    """Convert mg/dL to mmol/L."""
    return round(mgdl / 18.0, 1)


def mmol_to_mgdl(mmol: float) -> float:
    """Convert mmol/L to mg/dL."""
    return round(mmol * 18.0, 0)


def get_sensor_icon(sensor_type: str) -> str:
    """Get icon for sensor type."""
    icons = {
        "blood_sugar": "mdi:water",
        "insulin_on_board": "mdi:needle",
        "carbs_on_board": "mdi:food-apple",
        "sensitivity_ratio": "mdi:chart-line-variant",
        "ea1c_24h": "mdi:chart-line",
        "ea1c_7d": "mdi:chart-line",
        "ea1c_30d": "mdi:chart-line",
        "ea1c_90d": "mdi:chart-line",
        "pump_reservoir": "mdi:water-outline",
        "pump_battery": "mdi:battery",
        "phone_battery": "mdi:cellphone-charging",
        "basal_rate": "mdi:water-pump",
        "temp_basal": "mdi:water-pump-off",
        "last_treatment": "mdi:clipboard-text-clock",
        "last_bolus": "mdi:needle",
        "last_carbs": "mdi:food",
        "loop_status": "mdi:sync",
        "device_status": "mdi:devices",
    }
    return icons.get(sensor_type, "mdi:help-circle")


def get_bg_state(value: float, low: int = 70, high: int = 180) -> str:
    """Get blood glucose state."""
    if value < low:
        return "low"
    elif value > high:
        return "high"
    return "normal"


def round_to_precision(value: float | None, precision: int = 1) -> float | None:
    """Round value to specified precision."""
    if value is None:
        return None
    return round(value, precision)
