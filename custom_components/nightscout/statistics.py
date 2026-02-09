"""Statistical calculations for Nightscout data."""
from __future__ import annotations

import logging
import statistics
from typing import Any

_LOGGER = logging.getLogger(__name__)


def mgdl_to_mmol(mgdl: float) -> float:
    """Convert mg/dL to mmol/L."""
    return round(mgdl / 18.0, 1)


def mmol_to_mgdl(mmol: float) -> float:
    """Convert mmol/L to mg/dL."""
    return round(mmol * 18.0, 0)


class GlucoseStatistics:
    """Class for calculating glucose statistics."""

    def __init__(
        self,
        entries: list[dict[str, Any]],
        target_min: float = 70,
        target_max: float = 180,
        unit: str = "mg/dL",
    ) -> None:
        """Initialize glucose statistics calculator.
        
        Args:
            entries: List of glucose entries from Nightscout API
            target_min: Lower bound of target range (mg/dL)
            target_max: Upper bound of target range (mg/dL)
            unit: Unit of measurement ('mg/dL' or 'mmol/L')
        """
        self.entries = entries
        self.target_min = target_min
        self.target_max = target_max
        self.unit = unit
        self.glucose_values = self._extract_glucose_values()

    def _extract_glucose_values(self) -> list[float]:
        """Extract glucose values from entries."""
        values = []
        for entry in self.entries:
            if "sgv" in entry and entry["sgv"] is not None:
                values.append(float(entry["sgv"]))
        return values

    def calculate_ea1c(self) -> float | None:
        """Calculate eA1c (estimated A1c) using GMI formula.
        
        GMI formula: eA1c(%) = 3.31 + 0.02392 × [average glucose in mg/dL]
        
        Returns:
            eA1c percentage or None if no data
        """
        if not self.glucose_values:
            return None

        avg_glucose = statistics.mean(self.glucose_values)
        ea1c = 3.31 + (0.02392 * avg_glucose)
        return round(ea1c, 1)

    def calculate_time_in_range(self) -> dict[str, float]:
        """Calculate time in range statistics.
        
        Returns:
            Dictionary with percentages for in_range, below_range, above_range
        """
        if not self.glucose_values:
            return {
                "time_in_range": 0.0,
                "time_below_range": 0.0,
                "time_above_range": 0.0,
            }

        total = len(self.glucose_values)
        in_range = sum(1 for v in self.glucose_values if self.target_min <= v <= self.target_max)
        below_range = sum(1 for v in self.glucose_values if v < self.target_min)
        above_range = sum(1 for v in self.glucose_values if v > self.target_max)

        return {
            "time_in_range": round((in_range / total) * 100, 1),
            "time_below_range": round((below_range / total) * 100, 1),
            "time_above_range": round((above_range / total) * 100, 1),
        }

    def calculate_mean_bg(self) -> float | None:
        """Calculate mean blood glucose.
        
        Returns:
            Mean glucose value or None if no data
        """
        if not self.glucose_values:
            return None

        mean_val = statistics.mean(self.glucose_values)
        if self.unit == "mmol/L":
            return mgdl_to_mmol(mean_val)
        return round(mean_val, 1)

    def calculate_median_bg(self) -> float | None:
        """Calculate median blood glucose.
        
        Returns:
            Median glucose value or None if no data
        """
        if not self.glucose_values:
            return None

        median_val = statistics.median(self.glucose_values)
        if self.unit == "mmol/L":
            return mgdl_to_mmol(median_val)
        return round(median_val, 1)

    def calculate_stdev(self) -> float | None:
        """Calculate standard deviation of blood glucose.
        
        Returns:
            Standard deviation or None if insufficient data
        """
        if len(self.glucose_values) < 2:
            return None

        stdev_val = statistics.stdev(self.glucose_values)
        if self.unit == "mmol/L":
            return mgdl_to_mmol(stdev_val)
        return round(stdev_val, 1)

    def calculate_cv(self) -> float | None:
        """Calculate coefficient of variation (CV).
        
        CV = (Standard Deviation / Mean) × 100
        
        Returns:
            CV percentage or None if insufficient data
        """
        if len(self.glucose_values) < 2:
            return None

        mean_val = statistics.mean(self.glucose_values)
        stdev_val = statistics.stdev(self.glucose_values)

        if mean_val == 0:
            return None

        cv = (stdev_val / mean_val) * 100
        return round(cv, 1)

    def calculate_gvi(self) -> float | None:
        """Calculate Glycemic Variability Index (GVI).
        
        GVI is calculated based on the length of the glucose curve.
        Higher values indicate more variability.
        
        Returns:
            GVI value or None if insufficient data
        """
        if len(self.glucose_values) < 2:
            return None

        # Calculate total variation as sum of absolute differences
        total_variation = sum(
            abs(self.glucose_values[i] - self.glucose_values[i - 1])
            for i in range(1, len(self.glucose_values))
        )

        # Normalize by number of measurements
        gvi = total_variation / len(self.glucose_values)
        return round(gvi, 2)

    def calculate_pgs(self) -> float | None:
        """Calculate Patient Glycemic Status (PGS).
        
        PGS combines mean glucose and variability.
        PGS = Mean + (Variability Factor × StdDev)
        
        Returns:
            PGS value or None if insufficient data
        """
        if len(self.glucose_values) < 2:
            return None

        mean_val = statistics.mean(self.glucose_values)
        stdev_val = statistics.stdev(self.glucose_values)

        # Variability factor (typically 1.0)
        variability_factor = 1.0
        pgs = mean_val + (variability_factor * stdev_val)

        if self.unit == "mmol/L":
            return mgdl_to_mmol(pgs)
        return round(pgs, 1)

    def get_all_statistics(self) -> dict[str, Any]:
        """Calculate all statistics at once.
        
        Returns:
            Dictionary with all calculated statistics
        """
        tir = self.calculate_time_in_range()
        
        return {
            "ea1c": self.calculate_ea1c(),
            "mean_bg": self.calculate_mean_bg(),
            "median_bg": self.calculate_median_bg(),
            "stdev": self.calculate_stdev(),
            "cv": self.calculate_cv(),
            "gvi": self.calculate_gvi(),
            "pgs": self.calculate_pgs(),
            "time_in_range": tir["time_in_range"],
            "time_below_range": tir["time_below_range"],
            "time_above_range": tir["time_above_range"],
            "samples": len(self.glucose_values),
            "unit": self.unit,
        }


def calculate_statistics_for_period(
    entries: list[dict[str, Any]],
    target_min: float = 70,
    target_max: float = 180,
    unit: str = "mg/dL",
) -> dict[str, Any]:
    """Calculate statistics for a given period of entries.
    
    Args:
        entries: List of glucose entries from Nightscout API
        target_min: Lower bound of target range (default: 70 mg/dL or 3.9 mmol/L)
        target_max: Upper bound of target range (default: 180 mg/dL or 10.0 mmol/L)
        unit: Unit of measurement ('mg/dL' or 'mmol/L')
    
    Returns:
        Dictionary with all calculated statistics
    """
    # Convert mmol/L targets to mg/dL if needed
    if unit == "mmol/L":
        target_min_mgdl = mmol_to_mgdl(target_min) if target_min < 20 else target_min
        target_max_mgdl = mmol_to_mgdl(target_max) if target_max < 20 else target_max
    else:
        target_min_mgdl = target_min
        target_max_mgdl = target_max

    stats_calculator = GlucoseStatistics(
        entries=entries,
        target_min=target_min_mgdl,
        target_max=target_max_mgdl,
        unit=unit,
    )

    return stats_calculator.get_all_statistics()
