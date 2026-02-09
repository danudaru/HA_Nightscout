"""Report generation for Nightscout data."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

_LOGGER = logging.getLogger(__name__)


class NightscoutReports:
    """Class for generating Nightscout reports."""

    def __init__(self, api: Any) -> None:
        """Initialize the reports generator."""
        self.api = api

    async def get_daily_report(self, date: datetime | None = None) -> dict[str, Any]:
        """Generate daily report.
        
        Args:
            date: Date for the report (default: today)
            
        Returns:
            Dictionary with daily statistics
        """
        if date is None:
            date = datetime.now()

        # Get entries for the day (last 24 hours)
        entries = await self.api.get_entries_for_period(24)
        
        if not entries:
            return {"error": "No data available"}

        from .statistics import calculate_statistics_for_period

        stats = calculate_statistics_for_period(entries)
        
        return {
            "report_type": "daily",
            "date": date.strftime("%Y-%m-%d"),
            "period": "24 hours",
            **stats,
        }

    async def get_weekly_report(self, weeks_ago: int = 0) -> dict[str, Any]:
        """Generate weekly report.
        
        Args:
            weeks_ago: Number of weeks ago (0 = current week)
            
        Returns:
            Dictionary with weekly statistics
        """
        hours = 168 + (weeks_ago * 168)  # 7 days * 24 hours
        entries = await self.api.get_entries_for_period(hours)
        
        # Filter to get only the specific week
        if weeks_ago > 0:
            start_time = datetime.now() - timedelta(hours=hours)
            end_time = datetime.now() - timedelta(hours=weeks_ago * 168)
            
            entries = [
                e for e in entries
                if start_time.timestamp() * 1000 <= e.get("date", 0) <= end_time.timestamp() * 1000
            ]

        if not entries:
            return {"error": "No data available"}

        from .statistics import calculate_statistics_for_period

        stats = calculate_statistics_for_period(entries)
        
        return {
            "report_type": "weekly",
            "weeks_ago": weeks_ago,
            "period": "7 days",
            **stats,
        }

    async def get_monthly_report(self, months_ago: int = 0) -> dict[str, Any]:
        """Generate monthly report.
        
        Args:
            months_ago: Number of months ago (0 = current month)
            
        Returns:
            Dictionary with monthly statistics
        """
        hours = 720 + (months_ago * 720)  # ~30 days * 24 hours
        entries = await self.api.get_entries_for_period(hours)
        
        if months_ago > 0:
            start_time = datetime.now() - timedelta(hours=hours)
            end_time = datetime.now() - timedelta(hours=months_ago * 720)
            
            entries = [
                e for e in entries
                if start_time.timestamp() * 1000 <= e.get("date", 0) <= end_time.timestamp() * 1000
            ]

        if not entries:
            return {"error": "No data available"}

        from .statistics import calculate_statistics_for_period

        stats = calculate_statistics_for_period(entries)
        
        return {
            "report_type": "monthly",
            "months_ago": months_ago,
            "period": "30 days",
            **stats,
        }

    async def get_quarterly_report(self, quarters_ago: int = 0) -> dict[str, Any]:
        """Generate quarterly report (90 days).
        
        Args:
            quarters_ago: Number of quarters ago (0 = current quarter)
            
        Returns:
            Dictionary with quarterly statistics
        """
        hours = 2160 + (quarters_ago * 2160)  # ~90 days * 24 hours
        entries = await self.api.get_entries_for_period(hours)
        
        if quarters_ago > 0:
            start_time = datetime.now() - timedelta(hours=hours)
            end_time = datetime.now() - timedelta(hours=quarters_ago * 2160)
            
            entries = [
                e for e in entries
                if start_time.timestamp() * 1000 <= e.get("date", 0) <= end_time.timestamp() * 1000
            ]

        if not entries:
            return {"error": "No data available"}

        from .statistics import calculate_statistics_for_period

        stats = calculate_statistics_for_period(entries)
        
        return {
            "report_type": "quarterly",
            "quarters_ago": quarters_ago,
            "period": "90 days",
            **stats,
        }

    async def get_comparison_report(
        self, period1_hours: int, period2_hours: int
    ) -> dict[str, Any]:
        """Generate comparison report between two periods.
        
        Args:
            period1_hours: Hours for first period
            period2_hours: Hours for second period
            
        Returns:
            Dictionary with comparison statistics
        """
        entries1 = await self.api.get_entries_for_period(period1_hours)
        entries2 = await self.api.get_entries_for_period(period2_hours)

        from .statistics import calculate_statistics_for_period

        stats1 = calculate_statistics_for_period(entries1)
        stats2 = calculate_statistics_for_period(entries2)

        # Calculate differences
        differences = {}
        for key in ["mean_bg", "ea1c", "time_in_range", "cv"]:
            if key in stats1 and key in stats2:
                if stats1[key] is not None and stats2[key] is not None:
                    differences[f"{key}_change"] = round(
                        stats1[key] - stats2[key], 1
                    )

        return {
            "report_type": "comparison",
            "period1": {"hours": period1_hours, **stats1},
            "period2": {"hours": period2_hours, **stats2},
            "differences": differences,
        }


# Report categories for organization
REPORT_CATEGORIES = {
    "time_based": {
        "name": "Time-based Reports",
        "description": "Reports organized by time period",
        "reports": [
            {"id": "daily", "name": "Daily Report", "period_hours": 24},
            {"id": "weekly", "name": "Weekly Report", "period_hours": 168},
            {"id": "monthly", "name": "Monthly Report", "period_hours": 720},
            {"id": "quarterly", "name": "Quarterly Report", "period_hours": 2160},
        ],
    },
    "glucose_control": {
        "name": "Glucose Control Reports",
        "description": "Reports focused on glucose management",
        "reports": [
            {"id": "time_in_range", "name": "Time in Range Analysis"},
            {"id": "variability", "name": "Glucose Variability Report"},
            {"id": "trends", "name": "Trend Analysis"},
        ],
    },
    "insulin_carbs": {
        "name": "Insulin & Carbs Reports",
        "description": "Reports about insulin and carbohydrate management",
        "reports": [
            {"id": "insulin_summary", "name": "Insulin Usage Summary"},
            {"id": "carbs_summary", "name": "Carbohydrate Intake Summary"},
            {"id": "bolus_analysis", "name": "Bolus Analysis"},
        ],
    },
    "diagnostics": {
        "name": "System Diagnostics",
        "description": "Technical and system health reports",
        "reports": [
            {"id": "device_status", "name": "Device Status Report"},
            {"id": "data_quality", "name": "Data Quality Report"},
            {"id": "connectivity", "name": "Connectivity Status"},
        ],
    },
}


def get_report_categories() -> dict[str, Any]:
    """Get all available report categories.
    
    Returns:
        Dictionary of report categories and their reports
    """
    return REPORT_CATEGORIES
