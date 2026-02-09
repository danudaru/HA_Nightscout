"""Statistical sensors for Nightscout integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NightscoutDataUpdateCoordinator
from .const import (
    ATTR_CV,
    ATTR_GVI,
    ATTR_MEAN_BG,
    ATTR_MEDIAN_BG,
    ATTR_PGS,
    ATTR_SAMPLES,
    ATTR_STATUS_COLOR,
    ATTR_STDEV,
    ATTR_TIME_ABOVE_RANGE,
    ATTR_TIME_BELOW_RANGE,
    ATTR_TIME_IN_RANGE,
    ATTR_UNIT,
    DOMAIN,
    UNIT_MGDL,
    UNIT_MMOL,
)
from .defaults import (
    CV_REFERENCE_RANGES,
    EA1C_REFERENCE_RANGES,
    GVI_REFERENCE_RANGES,
    MEAN_BG_REFERENCE_RANGES,
    STDEV_REFERENCE_RANGES,
    TIR_REFERENCE_RANGES,
    get_status_color,
)
from .statistics import calculate_statistics_for_period

_LOGGER = logging.getLogger(__name__)


class StatisticalSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for statistical sensors."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        sensor_type: str,
        period_name: str,
        period_hours: int,
        glucose_unit: str,
        target_min: float,
        target_max: float,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._period_name = period_name
        self._period_hours = period_hours
        self._glucose_unit = glucose_unit
        self._target_min = target_min
        self._target_max = target_max
        self._attr_unique_id = f"nightscout_{sensor_type}_{period_name}"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "nightscout")},
            "name": "Nightscout",
            "manufacturer": "Nightscout Foundation",
            "model": "CGM Monitor",
        }

    def _get_entries(self) -> list[dict[str, Any]]:
        """Get entries for the period."""
        key_map = {
            "24h": "entries_24h",
            "7d": "entries_7d",
            "30d": "entries_30d",
            "90d": "entries_90d",
        }
        key = key_map.get(self._period_name, "entries_24h")
        return self.coordinator.data.get(key, [])

    def _get_statistics(self) -> dict[str, Any]:
        """Calculate statistics for the period."""
        entries = self._get_entries()
        if not entries:
            return {}

        return calculate_statistics_for_period(
            entries=entries,
            target_min=self._target_min,
            target_max=self._target_max,
            unit=self._glucose_unit,
        )


class MeanBGSensor(StatisticalSensorBase):
    """Mean blood glucose sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        period_name: str,
        period_hours: int,
        glucose_unit: str,
        target_min: float,
        target_max: float,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "mean_bg",
            period_name,
            period_hours,
            glucose_unit,
            target_min,
            target_max,
        )
        self._attr_name = f"Mean BG ({period_name})"
        self._attr_native_unit_of_measurement = (
            UNIT_MMOL if glucose_unit == UNIT_MMOL else UNIT_MGDL
        )
        self._attr_icon = "mdi:chart-line"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        stats = self._get_statistics()
        return stats.get("mean_bg")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self._get_statistics()
        mean_bg = stats.get("mean_bg")
        
        attrs = {
            ATTR_SAMPLES: stats.get("samples", 0),
            ATTR_UNIT: stats.get("unit", "mg/dL"),
        }

        if mean_bg is not None:
            attrs[ATTR_STATUS_COLOR] = get_status_color(mean_bg, MEAN_BG_REFERENCE_RANGES)

        return attrs


class MedianBGSensor(StatisticalSensorBase):
    """Median blood glucose sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        period_name: str,
        period_hours: int,
        glucose_unit: str,
        target_min: float,
        target_max: float,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "median_bg",
            period_name,
            period_hours,
            glucose_unit,
            target_min,
            target_max,
        )
        self._attr_name = f"Median BG ({period_name})"
        self._attr_native_unit_of_measurement = (
            UNIT_MMOL if glucose_unit == UNIT_MMOL else UNIT_MGDL
        )
        self._attr_icon = "mdi:chart-timeline-variant"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        stats = self._get_statistics()
        return stats.get("median_bg")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self._get_statistics()
        return {
            ATTR_SAMPLES: stats.get("samples", 0),
            ATTR_UNIT: stats.get("unit", "mg/dL"),
        }


class StdDevSensor(StatisticalSensorBase):
    """Standard deviation sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        period_name: str,
        period_hours: int,
        glucose_unit: str,
        target_min: float,
        target_max: float,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "stdev",
            period_name,
            period_hours,
            glucose_unit,
            target_min,
            target_max,
        )
        self._attr_name = f"StdDev ({period_name})"
        self._attr_native_unit_of_measurement = (
            UNIT_MMOL if glucose_unit == UNIT_MMOL else UNIT_MGDL
        )
        self._attr_icon = "mdi:chart-bell-curve"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        stats = self._get_statistics()
        return stats.get("stdev")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self._get_statistics()
        stdev = stats.get("stdev")
        
        attrs = {
            ATTR_SAMPLES: stats.get("samples", 0),
            ATTR_UNIT: stats.get("unit", "mg/dL"),
        }

        if stdev is not None:
            attrs[ATTR_STATUS_COLOR] = get_status_color(stdev, STDEV_REFERENCE_RANGES)

        return attrs


class CVSensor(StatisticalSensorBase):
    """Coefficient of variation sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        period_name: str,
        period_hours: int,
        glucose_unit: str,
        target_min: float,
        target_max: float,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "cv",
            period_name,
            period_hours,
            glucose_unit,
            target_min,
            target_max,
        )
        self._attr_name = f"CV ({period_name})"
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:percent"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        stats = self._get_statistics()
        return stats.get("cv")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self._get_statistics()
        cv = stats.get("cv")
        
        attrs = {
            ATTR_SAMPLES: stats.get("samples", 0),
            ATTR_MEAN_BG: stats.get("mean_bg"),
            ATTR_STDEV: stats.get("stdev"),
        }

        if cv is not None:
            attrs[ATTR_STATUS_COLOR] = get_status_color(cv, CV_REFERENCE_RANGES)

        return attrs


class GVISensor(StatisticalSensorBase):
    """Glycemic Variability Index sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        period_name: str,
        period_hours: int,
        glucose_unit: str,
        target_min: float,
        target_max: float,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "gvi",
            period_name,
            period_hours,
            glucose_unit,
            target_min,
            target_max,
        )
        self._attr_name = f"GVI ({period_name})"
        self._attr_native_unit_of_measurement = None
        self._attr_icon = "mdi:chart-scatter-plot"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        stats = self._get_statistics()
        return stats.get("gvi")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self._get_statistics()
        gvi = stats.get("gvi")
        
        attrs = {
            ATTR_SAMPLES: stats.get("samples", 0),
        }

        if gvi is not None:
            attrs[ATTR_STATUS_COLOR] = get_status_color(gvi, GVI_REFERENCE_RANGES)

        return attrs


class PGSSensor(StatisticalSensorBase):
    """Patient Glycemic Status sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        period_name: str,
        period_hours: int,
        glucose_unit: str,
        target_min: float,
        target_max: float,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "pgs",
            period_name,
            period_hours,
            glucose_unit,
            target_min,
            target_max,
        )
        self._attr_name = f"PGS ({period_name})"
        self._attr_native_unit_of_measurement = (
            UNIT_MMOL if glucose_unit == UNIT_MMOL else UNIT_MGDL
        )
        self._attr_icon = "mdi:account-heart"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        stats = self._get_statistics()
        return stats.get("pgs")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self._get_statistics()
        return {
            ATTR_SAMPLES: stats.get("samples", 0),
            ATTR_MEAN_BG: stats.get("mean_bg"),
            ATTR_STDEV: stats.get("stdev"),
            ATTR_UNIT: stats.get("unit", "mg/dL"),
        }


class TIRSensor(StatisticalSensorBase):
    """Time in range sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        period_name: str,
        period_hours: int,
        glucose_unit: str,
        target_min: float,
        target_max: float,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tir",
            period_name,
            period_hours,
            glucose_unit,
            target_min,
            target_max,
        )
        self._attr_name = f"Time in Range ({period_name})"
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:target"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        stats = self._get_statistics()
        return stats.get("time_in_range")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self._get_statistics()
        tir = stats.get("time_in_range")
        
        attrs = {
            ATTR_SAMPLES: stats.get("samples", 0),
            ATTR_TIME_BELOW_RANGE: stats.get("time_below_range"),
            ATTR_TIME_ABOVE_RANGE: stats.get("time_above_range"),
        }

        if tir is not None:
            attrs[ATTR_STATUS_COLOR] = get_status_color(
                tir, TIR_REFERENCE_RANGES["time_in_range"]
            )

        return attrs


class TBRSensor(StatisticalSensorBase):
    """Time below range sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        period_name: str,
        period_hours: int,
        glucose_unit: str,
        target_min: float,
        target_max: float,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tbr",
            period_name,
            period_hours,
            glucose_unit,
            target_min,
            target_max,
        )
        self._attr_name = f"Time Below Range ({period_name})"
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:arrow-down-bold"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        stats = self._get_statistics()
        return stats.get("time_below_range")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self._get_statistics()
        tbr = stats.get("time_below_range")
        
        attrs = {
            ATTR_SAMPLES: stats.get("samples", 0),
            ATTR_TIME_IN_RANGE: stats.get("time_in_range"),
            ATTR_TIME_ABOVE_RANGE: stats.get("time_above_range"),
        }

        if tbr is not None:
            # For TBR, lower is better, so we use reverse logic
            attrs[ATTR_STATUS_COLOR] = get_status_color(
                tbr, TIR_REFERENCE_RANGES["time_below_range"], reverse=True
            )

        return attrs


class TARSensor(StatisticalSensorBase):
    """Time above range sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        period_name: str,
        period_hours: int,
        glucose_unit: str,
        target_min: float,
        target_max: float,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tar",
            period_name,
            period_hours,
            glucose_unit,
            target_min,
            target_max,
        )
        self._attr_name = f"Time Above Range ({period_name})"
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:arrow-up-bold"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        stats = self._get_statistics()
        return stats.get("time_above_range")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self._get_statistics()
        tar = stats.get("time_above_range")
        
        attrs = {
            ATTR_SAMPLES: stats.get("samples", 0),
            ATTR_TIME_IN_RANGE: stats.get("time_in_range"),
            ATTR_TIME_BELOW_RANGE: stats.get("time_below_range"),
        }

        if tar is not None:
            # For TAR, lower is better, so we use reverse logic
            attrs[ATTR_STATUS_COLOR] = get_status_color(
                tar, TIR_REFERENCE_RANGES["time_above_range"], reverse=True
            )

        return attrs
