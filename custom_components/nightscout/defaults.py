"""Default settings and reference ranges for Nightscout metrics."""
from typing import Final

# Blood Glucose Reference Ranges (mg/dL)
BG_REFERENCE_RANGES: Final = {
    "target_range": {
        "min": 70,  # mg/dL (3.9 mmol/L)
        "max": 180,  # mg/dL (10.0 mmol/L)
        "description": "Target glucose range for diabetes management",
    },
    "hypoglycemia": {
        "level1": 70,  # mg/dL (3.9 mmol/L) - Alert level
        "level2": 54,  # mg/dL (3.0 mmol/L) - Clinically significant
        "description": "Low blood glucose thresholds",
    },
    "hyperglycemia": {
        "level1": 180,  # mg/dL (10.0 mmol/L) - Above target
        "level2": 250,  # mg/dL (13.9 mmol/L) - Clinically significant
        "description": "High blood glucose thresholds",
    },
}

# eA1c Reference Ranges
EA1C_REFERENCE_RANGES: Final = {
    "optimal": {
        "max": 5.7,
        "color": "green",
        "description": "Normal (Non-diabetic range)",
    },
    "prediabetes": {
        "min": 5.7,
        "max": 6.4,
        "color": "yellow",
        "description": "Prediabetes range",
    },
    "diabetes_good_control": {
        "min": 6.5,
        "max": 7.0,
        "color": "green",
        "description": "Diabetes - Good control",
    },
    "diabetes_acceptable": {
        "min": 7.0,
        "max": 8.0,
        "color": "yellow",
        "description": "Diabetes - Acceptable control",
    },
    "diabetes_poor_control": {
        "min": 8.0,
        "color": "red",
        "description": "Diabetes - Poor control, needs adjustment",
    },
}

# Time in Range Reference Values
TIR_REFERENCE_RANGES: Final = {
    "time_in_range": {
        "excellent": {
            "min": 70,
            "color": "green",
            "description": "Excellent glucose control",
        },
        "good": {
            "min": 50,
            "max": 70,
            "color": "lightgreen",
            "description": "Good glucose control",
        },
        "acceptable": {
            "min": 30,
            "max": 50,
            "color": "yellow",
            "description": "Acceptable, room for improvement",
        },
        "poor": {
            "max": 30,
            "color": "red",
            "description": "Poor control, needs intervention",
        },
    },
    "time_below_range": {
        "safe": {
            "max": 4,
            "color": "green",
            "description": "Safe level of hypoglycemia",
        },
        "elevated": {
            "min": 4,
            "max": 10,
            "color": "yellow",
            "description": "Elevated hypoglycemia risk",
        },
        "high": {
            "min": 10,
            "color": "red",
            "description": "High hypoglycemia risk",
        },
    },
    "time_above_range": {
        "safe": {
            "max": 25,
            "color": "green",
            "description": "Acceptable hyperglycemia time",
        },
        "elevated": {
            "min": 25,
            "max": 50,
            "color": "yellow",
            "description": "Elevated hyperglycemia",
        },
        "high": {
            "min": 50,
            "color": "red",
            "description": "Excessive hyperglycemia",
        },
    },
}

# Coefficient of Variation (CV) Reference Ranges
CV_REFERENCE_RANGES: Final = {
    "stable": {
        "max": 36,
        "color": "green",
        "description": "Stable glucose levels",
    },
    "moderate_variability": {
        "min": 36,
        "max": 50,
        "color": "yellow",
        "description": "Moderate glucose variability",
    },
    "high_variability": {
        "min": 50,
        "color": "red",
        "description": "High glucose variability",
    },
}

# Standard Deviation Reference Ranges (mg/dL)
STDEV_REFERENCE_RANGES: Final = {
    "low": {
        "max": 50,
        "color": "green",
        "description": "Low variability",
    },
    "moderate": {
        "min": 50,
        "max": 70,
        "color": "yellow",
        "description": "Moderate variability",
    },
    "high": {
        "min": 70,
        "color": "red",
        "description": "High variability",
    },
}

# GVI (Glycemic Variability Index) Reference Ranges
GVI_REFERENCE_RANGES: Final = {
    "low": {
        "max": 1.2,
        "color": "green",
        "description": "Low glycemic variability",
    },
    "moderate": {
        "min": 1.2,
        "max": 1.5,
        "color": "yellow",
        "description": "Moderate glycemic variability",
    },
    "high": {
        "min": 1.5,
        "color": "red",
        "description": "High glycemic variability",
    },
}

# PGS (Patient Glycemic Status) Reference Ranges
PGS_REFERENCE_RANGES: Final = {
    "excellent": {
        "max": 35,
        "color": "green",
        "description": "Excellent glycemic status (non-diabetic)",
    },
    "good": {
        "min": 35,
        "max": 100,
        "color": "lightgreen",
        "description": "Good glycemic status (diabetic)",
    },
    "poor": {
        "min": 100,
        "max": 150,
        "color": "yellow",
        "description": "Poor glycemic status (diabetic)",
    },
    "very_poor": {
        "min": 150,
        "color": "red",
        "description": "Very poor glycemic status (diabetic)",
    },
}

# Mean Blood Glucose Reference Ranges (mg/dL)
MEAN_BG_REFERENCE_RANGES: Final = {
    "target": {
        "min": 70,
        "max": 154,  # Corresponds to ~7% A1c
        "color": "green",
        "description": "Target mean glucose",
    },
    "acceptable": {
        "min": 154,
        "max": 183,  # Corresponds to ~8% A1c
        "color": "yellow",
        "description": "Acceptable mean glucose",
    },
    "high": {
        "min": 183,
        "color": "red",
        "description": "High mean glucose",
    },
    "low": {
        "max": 70,
        "color": "red",
        "description": "Mean glucose too low",
    },
}

# System Diagnostics Thresholds
DIAGNOSTIC_THRESHOLDS: Final = {
    "data_age": {
        "ok": {
            "max_minutes": 10,
            "color": "green",
            "description": "Data is fresh",
        },
        "warning": {
            "max_minutes": 25,
            "color": "yellow",
            "description": "Data is getting old",
        },
        "critical": {
            "min_minutes": 25,
            "color": "red",
            "description": "Data is stale",
        },
    },
    "database_size": {
        "ok": {
            "max_percent": 70,
            "color": "green",
            "description": "Database size is healthy",
        },
        "warning": {
            "max_percent": 90,
            "color": "yellow",
            "description": "Database approaching limit",
        },
        "critical": {
            "min_percent": 90,
            "color": "red",
            "description": "Database nearly full",
        },
    },
    "domain_expiry": {
        "ok": {
            "min_days": 30,
            "color": "green",
            "description": "Domain expiry is not soon",
        },
        "warning": {
            "min_days": 7,
            "color": "yellow",
            "description": "Domain expiring soon",
        },
        "critical": {
            "max_days": 7,
            "color": "red",
            "description": "Domain expiring very soon",
        },
    },
    "pump_reservoir": {
        "ok": {
            "min_units": 50,
            "color": "green",
            "description": "Adequate insulin in reservoir",
        },
        "warning": {
            "min_units": 20,
            "color": "yellow",
            "description": "Low insulin in reservoir",
        },
        "critical": {
            "max_units": 20,
            "color": "red",
            "description": "Very low insulin in reservoir",
        },
    },
    "battery": {
        "ok": {
            "min_percent": 30,
            "color": "green",
            "description": "Battery level is good",
        },
        "warning": {
            "min_percent": 15,
            "color": "yellow",
            "description": "Battery level is low",
        },
        "critical": {
            "max_percent": 15,
            "color": "red",
            "description": "Battery level is critical",
        },
    },
}

# Default Configuration Values
DEFAULT_CONFIG: Final = {
    "glucose_unit": "mg/dL",  # or "mmol/L"
    "target_range_min_mgdl": 70,
    "target_range_max_mgdl": 180,
    "target_range_min_mmol": 3.9,
    "target_range_max_mmol": 10.0,
    "update_interval_seconds": 60,
    "statistics_update_interval_hours": 6,
    "data_retention_days": 90,
    "enable_ddns": False,
    "ddns_service": None,  # "freedns" or "duckdns"
    "ddns_update_interval_hours": 24,
}

# Unit Conversion Constants
UNIT_CONVERSION: Final = {
    "mgdl_to_mmol": 18.0,  # Divide mg/dL by 18 to get mmol/L
    "mmol_to_mgdl": 18.0,  # Multiply mmol/L by 18 to get mg/dL
}


def get_status_color(value: float, ranges: dict, reverse: bool = False) -> str:
    """Get status color based on value and reference ranges.
    
    Args:
        value: The value to check
        ranges: Reference ranges dictionary
        reverse: If True, reverse the color logic (for metrics where lower is better)
        
    Returns:
        Color string ("green", "yellow", "red")
    """
    for range_name, range_data in ranges.items():
        min_val = range_data.get("min", float("-inf"))
        max_val = range_data.get("max", float("inf"))
        
        if min_val <= value <= max_val:
            color = range_data.get("color", "green")
            if reverse:
                # Reverse color logic for metrics where lower is better
                color_map = {"green": "red", "red": "green", "yellow": "yellow"}
                return color_map.get(color, color)
            return color
    
    return "gray"


def get_status_description(value: float, ranges: dict) -> str:
    """Get status description based on value and reference ranges.
    
    Args:
        value: The value to check
        ranges: Reference ranges dictionary
        
    Returns:
        Description string
    """
    for range_name, range_data in ranges.items():
        min_val = range_data.get("min", float("-inf"))
        max_val = range_data.get("max", float("inf"))
        
        if min_val <= value <= max_val:
            return range_data.get("description", "")
    
    return "Unknown status"
