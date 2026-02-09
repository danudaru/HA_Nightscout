"""Constants for the Nightscout Extended integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "nightscout"

# Configuration
CONF_URL: Final = "url"
CONF_API_KEY: Final = "api_key"

# Update intervals
UPDATE_INTERVAL: Final = 60  # seconds
STATISTICS_UPDATE_INTERVAL: Final = 21600  # 6 hours in seconds

# Default values
DEFAULT_NAME: Final = "Nightscout"

# Configuration options
CONF_GLUCOSE_UNIT: Final = "glucose_unit"
CONF_TARGET_MIN: Final = "target_min"
CONF_TARGET_MAX: Final = "target_max"
CONF_ENABLE_DDNS: Final = "enable_ddns"
CONF_DDNS_SERVICE: Final = "ddns_service"
CONF_DDNS_TOKEN: Final = "ddns_token"
CONF_DDNS_DOMAIN: Final = "ddns_domain"
CONF_DDNS_UPDATE_URL: Final = "ddns_update_url"
CONF_DOMAIN_EXPIRY: Final = "domain_expiry"
CONF_DDNS_LAST_UPDATE: Final = "ddns_last_update"

# API endpoints
ENDPOINT_ENTRIES: Final = "/api/v1/entries.json"
ENDPOINT_DEVICESTATUS: Final = "/api/v1/devicestatus.json"
ENDPOINT_TREATMENTS: Final = "/api/v1/treatments.json"
ENDPOINT_PROFILE: Final = "/api/v1/profile.json"
ENDPOINT_STATUS: Final = "/api/v1/status.json"

# Sensor types - Blood Glucose
SENSOR_BLOOD_GLUCOSE: Final = "blood_glucose"  # Renamed from blood_sugar
SENSOR_BLOOD_SUGAR: Final = "blood_glucose"  # Legacy alias

# Sensor types - Insulin & Carbs
SENSOR_IOB: Final = "insulin_on_board"
SENSOR_COB: Final = "carbs_on_board"
SENSOR_SENSITIVITY: Final = "sensitivity_ratio"

# Sensor types - eA1c (Glycated Hemoglobin)
SENSOR_EA1C_24H: Final = "ea1c_24h"
SENSOR_EA1C_7D: Final = "ea1c_7d"
SENSOR_EA1C_30D: Final = "ea1c_30d"
SENSOR_EA1C_90D: Final = "ea1c_90d"

# Sensor types - Statistical metrics
SENSOR_MEAN_BG_24H: Final = "mean_bg_24h"
SENSOR_MEAN_BG_7D: Final = "mean_bg_7d"
SENSOR_MEAN_BG_30D: Final = "mean_bg_30d"
SENSOR_MEAN_BG_90D: Final = "mean_bg_90d"
SENSOR_MEDIAN_BG_24H: Final = "median_bg_24h"
SENSOR_MEDIAN_BG_7D: Final = "median_bg_7d"
SENSOR_MEDIAN_BG_30D: Final = "median_bg_30d"
SENSOR_MEDIAN_BG_90D: Final = "median_bg_90d"
SENSOR_STDEV_24H: Final = "stdev_24h"
SENSOR_STDEV_7D: Final = "stdev_7d"
SENSOR_STDEV_30D: Final = "stdev_30d"
SENSOR_STDEV_90D: Final = "stdev_90d"
SENSOR_CV_24H: Final = "cv_24h"
SENSOR_CV_7D: Final = "cv_7d"
SENSOR_CV_30D: Final = "cv_30d"
SENSOR_CV_90D: Final = "cv_90d"
SENSOR_GVI_24H: Final = "gvi_24h"
SENSOR_GVI_7D: Final = "gvi_7d"
SENSOR_GVI_30D: Final = "gvi_30d"
SENSOR_GVI_90D: Final = "gvi_90d"
SENSOR_PGS_24H: Final = "pgs_24h"
SENSOR_PGS_7D: Final = "pgs_7d"
SENSOR_PGS_30D: Final = "pgs_30d"
SENSOR_PGS_90D: Final = "pgs_90d"
SENSOR_TIR_24H: Final = "tir_24h"
SENSOR_TIR_7D: Final = "tir_7d"
SENSOR_TIR_30D: Final = "tir_30d"
SENSOR_TIR_90D: Final = "tir_90d"
SENSOR_TBR_24H: Final = "tbr_24h"
SENSOR_TBR_7D: Final = "tbr_7d"
SENSOR_TBR_30D: Final = "tbr_30d"
SENSOR_TBR_90D: Final = "tbr_90d"
SENSOR_TAR_24H: Final = "tar_24h"
SENSOR_TAR_7D: Final = "tar_7d"
SENSOR_TAR_30D: Final = "tar_30d"
SENSOR_TAR_90D: Final = "tar_90d"

# Sensor types - Device status
SENSOR_PUMP_RESERVOIR: Final = "pump_reservoir"
SENSOR_PUMP_BATTERY: Final = "pump_battery"
SENSOR_PHONE_BATTERY: Final = "phone_battery"
SENSOR_BASAL_RATE: Final = "basal_rate"
SENSOR_TEMP_BASAL: Final = "temp_basal"

# Sensor types - Treatments
SENSOR_LAST_TREATMENT: Final = "last_treatment"
SENSOR_LAST_BOLUS: Final = "last_bolus"
SENSOR_LAST_CARBS: Final = "last_carbs"

# Sensor types - System status
SENSOR_LOOP_STATUS: Final = "loop_status"
SENSOR_DEVICE_STATUS: Final = "device_status"
SENSOR_SERVER_STATUS: Final = "server_status"
SENSOR_DATA_FRESHNESS: Final = "data_freshness"
SENSOR_DATABASE_SIZE: Final = "database_size"

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
ATTR_MEAN_BG: Final = "mean_bg"
ATTR_MEDIAN_BG: Final = "median_bg"
ATTR_STDEV: Final = "stdev"
ATTR_CV: Final = "cv"
ATTR_GVI: Final = "gvi"
ATTR_PGS: Final = "pgs"
ATTR_UNIT: Final = "unit"
ATTR_STATUS_COLOR: Final = "status_color"
ATTR_SERVER_AVAILABLE: Final = "server_available"
ATTR_DNS_RESOLVED: Final = "dns_resolved"
ATTR_DATA_AGE: Final = "data_age"
ATTR_DATABASE_SIZE: Final = "database_size"
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
