"""Constants for the Nightscout Extended integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "nightscout"

# Configuration
CONF_URL: Final = "url"
CONF_API_KEY: Final = "api_key"

# Update intervals
UPDATE_INTERVAL: Final = 60  # seconds

# Default values
DEFAULT_NAME: Final = "Nightscout"

# API endpoints
ENDPOINT_ENTRIES: Final = "/api/v1/entries.json"
ENDPOINT_DEVICESTATUS: Final = "/api/v1/devicestatus.json"
ENDPOINT_TREATMENTS: Final = "/api/v1/treatments.json"
ENDPOINT_PROFILE: Final = "/api/v1/profile.json"
ENDPOINT_STATUS: Final = "/api/v1/status.json"

# Sensor types
SENSOR_BLOOD_SUGAR: Final = "blood_sugar"
SENSOR_IOB: Final = "insulin_on_board"
SENSOR_COB: Final = "carbs_on_board"
SENSOR_SENSITIVITY: Final = "sensitivity_ratio"
SENSOR_EA1C_24H: Final = "ea1c_24h"
SENSOR_EA1C_7D: Final = "ea1c_7d"
SENSOR_EA1C_30D: Final = "ea1c_30d"
SENSOR_EA1C_90D: Final = "ea1c_90d"
SENSOR_PUMP_RESERVOIR: Final = "pump_reservoir"
SENSOR_PUMP_BATTERY: Final = "pump_battery"
SENSOR_PHONE_BATTERY: Final = "phone_battery"
SENSOR_BASAL_RATE: Final = "basal_rate"
SENSOR_TEMP_BASAL: Final = "temp_basal"
SENSOR_LAST_TREATMENT: Final = "last_treatment"
SENSOR_LAST_BOLUS: Final = "last_bolus"
SENSOR_LAST_CARBS: Final = "last_carbs"
SENSOR_LOOP_STATUS: Final = "loop_status"
SENSOR_DEVICE_STATUS: Final = "device_status"

# Blood sugar directions
DIRECTION_ICONS: Final = {
    "DoubleUp": "⇈",
    "SingleUp": "↑",
    "FortyFiveUp": "⤴",
    "Flat": "→",
    "FortyFiveDown": "⤵",
    "SingleDown": "↓",
    "DoubleDown": "⇊",
    "NONE": "⊝",
}

# Blood sugar units
UNIT_MGDL: Final = "mg/dL"
UNIT_MMOL: Final = "mmol/L"

# IOB/COB units
UNIT_INSULIN: Final = "U"
UNIT_CARBS: Final = "g"

# Battery unit
UNIT_BATTERY: Final = "%"

# Sensitivity ratio
UNIT_RATIO: Final = ""

# eA1c unit
UNIT_EA1C: Final = "%"

# Time periods for eA1c calculation (in hours)
PERIOD_24H: Final = 24
PERIOD_7D: Final = 168  # 7 * 24
PERIOD_30D: Final = 720  # 30 * 24
PERIOD_90D: Final = 2160  # 90 * 24

# Blood sugar thresholds (mg/dL)
BG_LOW: Final = 70
BG_TARGET_MIN: Final = 70
BG_TARGET_MAX: Final = 180
BG_HIGH: Final = 250

# Device attributes
ATTR_DEVICE: Final = "device"
ATTR_DIRECTION: Final = "direction"
ATTR_DELTA: Final = "delta"
ATTR_LAST_UPDATE: Final = "last_update"
ATTR_STATUS: Final = "status"
ATTR_IOB: Final = "iob"
ATTR_COB: Final = "cob"
ATTR_SENSITIVITY: Final = "sensitivity_ratio"
ATTR_RESERVOIR: Final = "reservoir"
ATTR_PUMP_BATTERY: Final = "pump_battery"
ATTR_PHONE_BATTERY: Final = "phone_battery"
ATTR_BASAL_RATE: Final = "basal_rate"
ATTR_TEMP_BASAL_RATE: Final = "temp_basal_rate"
ATTR_TEMP_BASAL_DURATION: Final = "temp_basal_duration"
ATTR_TREATMENT_TYPE: Final = "treatment_type"
ATTR_INSULIN_AMOUNT: Final = "insulin_amount"
ATTR_CARBS_AMOUNT: Final = "carbs_amount"
ATTR_NOTES: Final = "notes"
ATTR_ENTERED_BY: Final = "entered_by"
ATTR_AVERAGE_BG: Final = "average_bg"
ATTR_SAMPLES: Final = "samples"
ATTR_TIME_IN_RANGE: Final = "time_in_range"
ATTR_TIME_BELOW_RANGE: Final = "time_below_range"
ATTR_TIME_ABOVE_RANGE: Final = "time_above_range"
