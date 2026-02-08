"""Sensor platform for Nightscout Extended integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NightscoutDataUpdateCoordinator
from .const import (
    ATTR_AVERAGE_BG,
    ATTR_BASAL_RATE,
    ATTR_CARBS_AMOUNT,
    ATTR_COB,
    ATTR_DELTA,
    ATTR_DEVICE,
    ATTR_DIRECTION,
    ATTR_ENTERED_BY,
    ATTR_INSULIN_AMOUNT,
    ATTR_IOB,
    ATTR_LAST_UPDATE,
    ATTR_NOTES,
    ATTR_PHONE_BATTERY,
    ATTR_PUMP_BATTERY,
    ATTR_RESERVOIR,
    ATTR_SAMPLES,
    ATTR_SENSITIVITY,
    ATTR_STATUS,
    ATTR_TEMP_BASAL_DURATION,
    ATTR_TEMP_BASAL_RATE,
    ATTR_TIME_ABOVE_RANGE,
    ATTR_TIME_BELOW_RANGE,
    ATTR_TIME_IN_RANGE,
    ATTR_TREATMENT_TYPE,
    DOMAIN,
    SENSOR_BASAL_RATE,
    SENSOR_BLOOD_SUGAR,
    SENSOR_COB,
    SENSOR_DEVICE_STATUS,
    SENSOR_EA1C_24H,
    SENSOR_EA1C_30D,
    SENSOR_EA1C_7D,
    SENSOR_EA1C_90D,
    SENSOR_IOB,
    SENSOR_LAST_BOLUS,
    SENSOR_LAST_CARBS,
    SENSOR_LAST_TREATMENT,
    SENSOR_LOOP_STATUS,
    SENSOR_PHONE_BATTERY,
    SENSOR_PUMP_BATTERY,
    SENSOR_PUMP_RESERVOIR,
    SENSOR_SENSITIVITY,
    SENSOR_TEMP_BASAL,
    UNIT_BATTERY,
    UNIT_CARBS,
    UNIT_EA1C,
    UNIT_INSULIN,
    UNIT_MGDL,
    UNIT_RATIO,
)
from .utils import (
    format_timestamp,
    get_bg_state,
    get_direction_icon,
    get_sensor_icon,
    round_to_precision,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nightscout sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]

    entities = [
        BloodSugarSensor(coordinator, api),
        IOBSensor(coordinator, api),
        COBSensor(coordinator, api),
        SensitivityRatioSensor(coordinator, api),
        EA1CSensor(coordinator, api, SENSOR_EA1C_24H, "24h", 24),
        EA1CSensor(coordinator, api, SENSOR_EA1C_7D, "7d", 168),
        EA1CSensor(coordinator, api, SENSOR_EA1C_30D, "30d", 720),
        EA1CSensor(coordinator, api, SENSOR_EA1C_90D, "90d", 2160),
        PumpReservoirSensor(coordinator, api),
        PumpBatterySensor(coordinator, api),
        PhoneBatterySensor(coordinator, api),
        BasalRateSensor(coordinator, api),
        TempBasalSensor(coordinator, api),
        LastTreatmentSensor(coordinator, api),
        LastBolusSensor(coordinator, api),
        LastCarbsSensor(coordinator, api),
        LoopStatusSensor(coordinator, api),
        DeviceStatusSensor(coordinator, api),
    ]

    async_add_entities(entities, True)


class NightscoutSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Nightscout sensors."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        api: Any,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.api = api
        self._sensor_type = sensor_type
        self._attr_unique_id = f"nightscout_{sensor_type}"
        self._attr_icon = get_sensor_icon(sensor_type)

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "nightscout")},
            "name": "Nightscout",
            "manufacturer": "Nightscout Foundation",
            "model": "CGM Monitor",
        }


class BloodSugarSensor(NightscoutSensorBase):
    """Blood sugar sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_BLOOD_SUGAR)
        self._attr_name = "Blood Sugar"
        self._attr_native_unit_of_measurement = UNIT_MGDL
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = None

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        entries = self.coordinator.data.get("entries", [])
        bg_data = self.api.extract_blood_sugar(entries)
        if bg_data:
            return bg_data.get("value")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        entries = self.coordinator.data.get("entries", [])
        bg_data = self.api.extract_blood_sugar(entries)
        if not bg_data:
            return {}

        value = bg_data.get("value")
        direction = bg_data.get("direction")
        
        return {
            ATTR_DIRECTION: f"{direction} {get_direction_icon(direction)}",
            ATTR_DELTA: round_to_precision(bg_data.get("delta"), 1),
            ATTR_DEVICE: bg_data.get("device"),
            ATTR_LAST_UPDATE: format_timestamp(bg_data.get("timestamp")),
            ATTR_STATUS: get_bg_state(value) if value else "unknown",
        }

    @property
    def icon(self) -> str:
        """Return icon based on blood sugar level."""
        value = self.native_value
        if value is None:
            return "mdi:water-alert"
        
        if value < 70:
            return "mdi:arrow-down-bold"
        elif value > 180:
            return "mdi:arrow-up-bold"
        return "mdi:water"


class IOBSensor(NightscoutSensorBase):
    """Insulin on board sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_IOB)
        self._attr_name = "Nightscout Insulin on Board"
        self._attr_native_unit_of_measurement = UNIT_INSULIN
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        iob = self.api.extract_iob(devicestatus)
        return round_to_precision(iob, 2) if iob is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        if devicestatus:
            return {
                ATTR_LAST_UPDATE: devicestatus[0].get("created_at"),
                ATTR_DEVICE: devicestatus[0].get("device"),
            }
        return {}


class COBSensor(NightscoutSensorBase):
    """Carbs on board sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_COB)
        self._attr_name = "Nightscout Carbs on Board"
        self._attr_native_unit_of_measurement = UNIT_CARBS
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        cob = self.api.extract_cob(devicestatus)
        return round_to_precision(cob, 1) if cob is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        if devicestatus:
            return {
                ATTR_LAST_UPDATE: devicestatus[0].get("created_at"),
                ATTR_DEVICE: devicestatus[0].get("device"),
            }
        return {}


class SensitivityRatioSensor(NightscoutSensorBase):
    """Sensitivity ratio sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_SENSITIVITY)
        self._attr_name = "Nightscout Sensitivity Ratio"
        self._attr_native_unit_of_measurement = UNIT_RATIO
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        sensitivity = self.api.extract_sensitivity_ratio(devicestatus)
        return round_to_precision(sensitivity, 2) if sensitivity is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        if devicestatus:
            return {
                ATTR_LAST_UPDATE: devicestatus[0].get("created_at"),
            }
        return {}


class EA1CSensor(NightscoutSensorBase):
    """Estimated A1c sensor."""

    def __init__(
        self,
        coordinator: NightscoutDataUpdateCoordinator,
        api: Any,
        sensor_type: str,
        period_name: str,
        period_hours: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, sensor_type)
        self._period_name = period_name
        self._period_hours = period_hours
        self._attr_name = f"Nightscout eA1c ({period_name})"
        self._attr_native_unit_of_measurement = UNIT_EA1C
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        # Get entries for the period
        key = f"entries_{self._period_name}"
        entries = self.coordinator.data.get(key, [])
        
        ea1c = self.api.calculate_ea1c(entries)
        return ea1c

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        key = f"entries_{self._period_name}"
        entries = self.coordinator.data.get(key, [])
        
        if not entries:
            return {}

        # Calculate average BG
        glucose_values = [e.get("sgv") for e in entries if e.get("sgv")]
        avg_bg = sum(glucose_values) / len(glucose_values) if glucose_values else None

        # Calculate time in range
        tir = self.api.calculate_time_in_range(entries)

        return {
            ATTR_AVERAGE_BG: round_to_precision(avg_bg, 0) if avg_bg else None,
            ATTR_SAMPLES: len(glucose_values),
            ATTR_TIME_IN_RANGE: tir.get("in_range"),
            ATTR_TIME_BELOW_RANGE: tir.get("below_range"),
            ATTR_TIME_ABOVE_RANGE: tir.get("above_range"),
        }


class PumpReservoirSensor(NightscoutSensorBase):
    """Pump reservoir sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_PUMP_RESERVOIR)
        self._attr_name = "Nightscout Pump Reservoir"
        self._attr_native_unit_of_measurement = UNIT_INSULIN
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = None

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        pump_data = self.api.extract_pump_data(devicestatus)
        if pump_data:
            reservoir = pump_data.get("reservoir")
            return round_to_precision(reservoir, 1) if reservoir is not None else None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        if devicestatus:
            return {
                ATTR_LAST_UPDATE: devicestatus[0].get("created_at"),
            }
        return {}


class PumpBatterySensor(NightscoutSensorBase):
    """Pump battery sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_PUMP_BATTERY)
        self._attr_name = "Nightscout Pump Battery"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.BATTERY

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        pump_data = self.api.extract_pump_data(devicestatus)
        if pump_data:
            return pump_data.get("battery")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        if devicestatus:
            return {
                ATTR_LAST_UPDATE: devicestatus[0].get("created_at"),
            }
        return {}


class PhoneBatterySensor(NightscoutSensorBase):
    """Phone battery sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_PHONE_BATTERY)
        self._attr_name = "Nightscout Phone Battery"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.BATTERY

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        return self.api.extract_phone_battery(devicestatus)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        if devicestatus:
            return {
                ATTR_LAST_UPDATE: devicestatus[0].get("created_at"),
            }
        return {}


class BasalRateSensor(NightscoutSensorBase):
    """Basal rate sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_BASAL_RATE)
        self._attr_name = "Nightscout Basal Rate"
        self._attr_native_unit_of_measurement = "U/h"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        pump_data = self.api.extract_pump_data(devicestatus)
        if pump_data:
            basal = pump_data.get("basal_rate")
            return round_to_precision(basal, 2) if basal is not None else None
        return None


class TempBasalSensor(NightscoutSensorBase):
    """Temporary basal sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_TEMP_BASAL)
        self._attr_name = "Nightscout Temp Basal"
        self._attr_native_unit_of_measurement = "U/h"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        temp_basal = self.api.extract_temp_basal(devicestatus)
        if temp_basal:
            rate = temp_basal.get("rate")
            return round_to_precision(rate, 2) if rate is not None else None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        temp_basal = self.api.extract_temp_basal(devicestatus)
        if temp_basal:
            return {
                ATTR_TEMP_BASAL_DURATION: temp_basal.get("duration"),
                ATTR_LAST_UPDATE: temp_basal.get("timestamp"),
            }
        return {}


class LastTreatmentSensor(NightscoutSensorBase):
    """Last treatment sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_LAST_TREATMENT)
        self._attr_name = "Nightscout Last Treatment"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        treatments = self.coordinator.data.get("treatments", [])
        treatment = self.api.extract_last_treatment(treatments)
        if treatment:
            return treatment.get("event_type", "Unknown")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        treatments = self.coordinator.data.get("treatments", [])
        treatment = self.api.extract_last_treatment(treatments)
        if treatment:
            return {
                ATTR_INSULIN_AMOUNT: treatment.get("insulin"),
                ATTR_CARBS_AMOUNT: treatment.get("carbs"),
                ATTR_NOTES: treatment.get("notes"),
                ATTR_ENTERED_BY: treatment.get("entered_by"),
                ATTR_LAST_UPDATE: treatment.get("created_at"),
            }
        return {}


class LastBolusSensor(NightscoutSensorBase):
    """Last bolus sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_LAST_BOLUS)
        self._attr_name = "Nightscout Last Bolus"
        self._attr_native_unit_of_measurement = UNIT_INSULIN

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        treatments = self.coordinator.data.get("treatments", [])
        # Look for bolus-related treatments
        for treatment in treatments:
            event_type = treatment.get("eventType", "")
            if "Bolus" in event_type and treatment.get("insulin"):
                return round_to_precision(treatment.get("insulin"), 2)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        treatments = self.coordinator.data.get("treatments", [])
        for treatment in treatments:
            event_type = treatment.get("eventType", "")
            if "Bolus" in event_type and treatment.get("insulin"):
                return {
                    ATTR_TREATMENT_TYPE: event_type,
                    ATTR_NOTES: treatment.get("notes"),
                    ATTR_LAST_UPDATE: treatment.get("created_at"),
                }
        return {}


class LastCarbsSensor(NightscoutSensorBase):
    """Last carbs sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_LAST_CARBS)
        self._attr_name = "Nightscout Last Carbs"
        self._attr_native_unit_of_measurement = UNIT_CARBS

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        treatments = self.coordinator.data.get("treatments", [])
        # Look for carb-related treatments
        for treatment in treatments:
            if treatment.get("carbs"):
                return round_to_precision(treatment.get("carbs"), 0)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        treatments = self.coordinator.data.get("treatments", [])
        for treatment in treatments:
            if treatment.get("carbs"):
                return {
                    ATTR_TREATMENT_TYPE: treatment.get("eventType"),
                    ATTR_NOTES: treatment.get("notes"),
                    ATTR_LAST_UPDATE: treatment.get("created_at"),
                }
        return {}


class LoopStatusSensor(NightscoutSensorBase):
    """Loop status sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_LOOP_STATUS)
        self._attr_name = "Nightscout Loop Status"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        loop_status = self.api.extract_loop_status(devicestatus)
        if loop_status:
            return loop_status.get("type", "Unknown")
        return "Inactive"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        loop_status = self.api.extract_loop_status(devicestatus)
        if loop_status:
            return {
                ATTR_DEVICE: loop_status.get("device"),
                ATTR_LAST_UPDATE: loop_status.get("timestamp"),
                "version": loop_status.get("version"),
            }
        return {}


class DeviceStatusSensor(NightscoutSensorBase):
    """Device status overview sensor."""

    def __init__(self, coordinator: NightscoutDataUpdateCoordinator, api: Any) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, api, SENSOR_DEVICE_STATUS)
        self._attr_name = "Nightscout Device Status"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        if devicestatus:
            return "Online"
        return "Offline"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devicestatus = self.coordinator.data.get("devicestatus", [])
        if not devicestatus:
            return {}

        status = devicestatus[0]
        
        # Extract various data points
        iob = self.api.extract_iob(devicestatus)
        cob = self.api.extract_cob(devicestatus)
        sensitivity = self.api.extract_sensitivity_ratio(devicestatus)
        pump_data = self.api.extract_pump_data(devicestatus)
        phone_battery = self.api.extract_phone_battery(devicestatus)

        attrs = {
            ATTR_DEVICE: status.get("device"),
            ATTR_LAST_UPDATE: status.get("created_at"),
        }

        if iob is not None:
            attrs[ATTR_IOB] = round_to_precision(iob, 2)
        if cob is not None:
            attrs[ATTR_COB] = round_to_precision(cob, 1)
        if sensitivity is not None:
            attrs[ATTR_SENSITIVITY] = round_to_precision(sensitivity, 2)
        if pump_data:
            if pump_data.get("reservoir") is not None:
                attrs[ATTR_RESERVOIR] = round_to_precision(pump_data["reservoir"], 1)
            if pump_data.get("battery") is not None:
                attrs[ATTR_PUMP_BATTERY] = pump_data["battery"]
            if pump_data.get("basal_rate") is not None:
                attrs[ATTR_BASAL_RATE] = round_to_precision(pump_data["basal_rate"], 2)
        if phone_battery is not None:
            attrs[ATTR_PHONE_BATTERY] = phone_battery

        return attrs
