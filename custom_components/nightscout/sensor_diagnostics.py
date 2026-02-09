"""Diagnostic sensors for Nightscout integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NightscoutDataUpdateCoordinator
from .const import (
    ATTR_DATA_AGE,
    ATTR_DATABASE_SIZE,
    ATTR_DNS_RESOLVED,
    ATTR_SERVER_AVAILABLE,
    ATTR_STATUS_COLOR,
    DOMAIN,
)
from .diagnostics import NightscoutDiagnostics

_LOGGER = logging.getLogger(__name__)


class DiagnosticSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for diagnostic sensors."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        diagnostics: NightscoutDiagnostics,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.diagnostics = diagnostics
        self._sensor_type = sensor_type
        self._attr_unique_id = f"nightscout_{sensor_type}"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "nightscout")},
            "name": "Nightscout",
            "manufacturer": "Nightscout Foundation",
            "model": "CGM Monitor",
        }


class ServerStatusSensor(DiagnosticSensorBase):
    """Server availability status sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        diagnostics: NightscoutDiagnostics,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, diagnostics, "server_status")
        self._attr_name = "Nightscout Server Status"
        self._attr_icon = "mdi:server"
        self._last_status = None

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        # This will be updated by coordinator
        if self._last_status:
            return self._last_status.get("status", "unknown")
        return "checking"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if self._last_status:
            return {
                ATTR_SERVER_AVAILABLE: self._last_status.get("available", False),
                "response_time": self._last_status.get("response_time"),
                "error": self._last_status.get("error"),
            }
        return {}

    async def async_update(self) -> None:
        """Update sensor."""
        self._last_status = await self.diagnostics.check_server_availability()


class DataFreshnessSensor(DiagnosticSensorBase):
    """Data freshness status sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        diagnostics: NightscoutDiagnostics,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, diagnostics, "data_freshness")
        self._attr_name = "Nightscout Data Freshness"
        self._attr_icon = "mdi:clock-check"
        self._last_status = None

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self._last_status:
            return self._last_status.get("overall_status", "unknown")
        return "checking"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if self._last_status:
            glucose_status = self._last_status.get("glucose", {})
            aaps_status = self._last_status.get("aaps", {})
            
            return {
                "glucose_age_minutes": glucose_status.get("age_minutes"),
                "glucose_status": glucose_status.get("status"),
                "glucose_message": glucose_status.get("message"),
                "aaps_age_minutes": aaps_status.get("age_minutes"),
                "aaps_status": aaps_status.get("status"),
                "aaps_message": aaps_status.get("message"),
                ATTR_STATUS_COLOR: self._get_status_color(
                    self._last_status.get("overall_status")
                ),
            }
        return {}

    def _get_status_color(self, status: str) -> str:
        """Get color based on status."""
        color_map = {
            "ok": "green",
            "warning": "yellow",
            "critical": "red",
            "error": "red",
        }
        return color_map.get(status, "gray")

    async def async_update(self) -> None:
        """Update sensor."""
        self._last_status = await self.diagnostics.check_data_freshness()


class DatabaseSizeSensor(DiagnosticSensorBase):
    """Database size monitoring sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        diagnostics: NightscoutDiagnostics,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, diagnostics, "database_size")
        self._attr_name = "Nightscout Database Size"
        self._attr_native_unit_of_measurement = "MB"
        self._attr_icon = "mdi:database"
        self._last_status = None

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self._last_status:
            return self._last_status.get("status", "unknown")
        return "monitoring"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if self._last_status:
            return {
                "limit_mb": self._last_status.get("limit_mb"),
                "warning_threshold_mb": self._last_status.get("warning_threshold_mb"),
                "critical_threshold_mb": self._last_status.get("critical_threshold_mb"),
                "message": self._last_status.get("message"),
                "error": self._last_status.get("error"),
            }
        return {}

    async def async_update(self) -> None:
        """Update sensor."""
        self._last_status = await self.diagnostics.get_database_size()
