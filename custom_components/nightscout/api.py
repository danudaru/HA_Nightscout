"""Nightscout API client."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from .const import (
    ENDPOINT_DEVICESTATUS,
    ENDPOINT_ENTRIES,
    ENDPOINT_PROFILE,
    ENDPOINT_STATUS,
    ENDPOINT_TREATMENTS,
)

_LOGGER = logging.getLogger(__name__)


class NightscoutAPI:
    """Nightscout API client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
        api_key: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self.session = session
        self.url = url.rstrip("/")
        self.api_key = api_key
        self._headers = {}
        if api_key:
            self._headers["API-SECRET"] = api_key

    async def _request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> Any:
        """Make a request to the Nightscout API."""
        url = f"{self.url}{endpoint}"
        try:
            async with self.session.get(
                url, headers=self._headers, params=params, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching data from %s: %s", url, err)
            raise
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout fetching data from %s", url)
            raise

    async def test_connection(self) -> bool:
        """Test connection to Nightscout."""
        try:
            data = await self._request(ENDPOINT_STATUS)
            return data is not None and "status" in data
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False

    async def get_entries(self, count: int = 1) -> list[dict[str, Any]]:
        """Get glucose entries."""
        try:
            return await self._request(ENDPOINT_ENTRIES, {"count": count})
        except Exception as err:
            _LOGGER.error("Error getting entries: %s", err)
            return []

    async def get_entries_for_period(self, hours: int) -> list[dict[str, Any]]:
        """Get glucose entries for a specific time period."""
        try:
            # Calculate timestamp for the period
            time_ago = datetime.now() - timedelta(hours=hours)
            timestamp = int(time_ago.timestamp() * 1000)
            
            # Get entries from specific time
            params = {
                "find[dateString][$gte]": time_ago.isoformat(),
                "count": 10000  # Large number to get all entries in period
            }
            return await self._request(ENDPOINT_ENTRIES, params)
        except Exception as err:
            _LOGGER.error("Error getting entries for period: %s", err)
            return []

    async def get_devicestatus(self, count: int = 1) -> list[dict[str, Any]]:
        """Get device status."""
        try:
            return await self._request(ENDPOINT_DEVICESTATUS, {"count": count})
        except Exception as err:
            _LOGGER.error("Error getting device status: %s", err)
            return []

    async def get_treatments(self, count: int = 10) -> list[dict[str, Any]]:
        """Get treatments."""
        try:
            return await self._request(ENDPOINT_TREATMENTS, {"count": count})
        except Exception as err:
            _LOGGER.error("Error getting treatments: %s", err)
            return []

    async def get_profile(self) -> dict[str, Any] | None:
        """Get profile."""
        try:
            profiles = await self._request(ENDPOINT_PROFILE)
            if profiles and isinstance(profiles, list) and len(profiles) > 0:
                return profiles[0]
            return None
        except Exception as err:
            _LOGGER.error("Error getting profile: %s", err)
            return None

    async def get_status(self) -> dict[str, Any] | None:
        """Get Nightscout status."""
        try:
            return await self._request(ENDPOINT_STATUS)
        except Exception as err:
            _LOGGER.error("Error getting status: %s", err)
            return None

    # Data extraction methods

    def extract_blood_sugar(self, entries: list[dict[str, Any]]) -> dict[str, Any] | None:
        """Extract blood sugar data from entries."""
        if not entries:
            return None

        entry = entries[0]
        return {
            "value": entry.get("sgv"),
            "direction": entry.get("direction", "NONE"),
            "delta": entry.get("delta"),
            "device": entry.get("device"),
            "date": entry.get("dateString"),
            "timestamp": entry.get("date"),
        }

    def extract_iob(self, devicestatus: list[dict[str, Any]]) -> float | None:
        """Extract IOB from device status."""
        if not devicestatus:
            return None

        status = devicestatus[0]

        # Try AndroidAPS/OpenAPS format
        if "openaps" in status:
            openaps = status["openaps"]
            # Try suggested first
            if "suggested" in openaps and "IOB" in openaps["suggested"]:
                return openaps["suggested"]["IOB"]
            # Try iob object
            if "iob" in openaps and "iob" in openaps["iob"]:
                return openaps["iob"]["iob"]
            # Try enacted
            if "enacted" in openaps and "IOB" in openaps["enacted"]:
                return openaps["enacted"]["IOB"]

        # Try Loop format
        if "loop" in status and "iob" in status["loop"]:
            iob_data = status["loop"]["iob"]
            if "iob" in iob_data:
                return iob_data["iob"]

        # Try pump format
        if "pump" in status and "iob" in status["pump"]:
            iob_data = status["pump"]["iob"]
            if isinstance(iob_data, dict):
                return iob_data.get("bolus", 0) + iob_data.get("basal", 0)
            return iob_data

        return None

    def extract_cob(self, devicestatus: list[dict[str, Any]]) -> float | None:
        """Extract COB from device status."""
        if not devicestatus:
            return None

        status = devicestatus[0]

        # Try AndroidAPS/OpenAPS format
        if "openaps" in status:
            openaps = status["openaps"]
            # Try suggested first
            if "suggested" in openaps and "COB" in openaps["suggested"]:
                return openaps["suggested"]["COB"]
            # Try enacted
            if "enacted" in openaps and "COB" in openaps["enacted"]:
                return openaps["enacted"]["COB"]

        # Try Loop format
        if "loop" in status and "cob" in status["loop"]:
            cob_data = status["loop"]["cob"]
            if "cob" in cob_data:
                return cob_data["cob"]

        return None

    def extract_sensitivity_ratio(
        self, devicestatus: list[dict[str, Any]]
    ) -> float | None:
        """Extract sensitivity ratio from device status."""
        if not devicestatus:
            return None

        status = devicestatus[0]

        # Try AndroidAPS/OpenAPS format
        if "openaps" in status:
            openaps = status["openaps"]
            if "suggested" in openaps and "sensitivityRatio" in openaps["suggested"]:
                return openaps["suggested"]["sensitivityRatio"]

        return None

    def extract_pump_data(
        self, devicestatus: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Extract pump data from device status."""
        if not devicestatus:
            return None

        status = devicestatus[0]

        if "pump" not in status:
            return None

        pump = status["pump"]
        result = {}

        # Reservoir
        if "reservoir" in pump:
            result["reservoir"] = pump["reservoir"]

        # Battery
        if "battery" in pump:
            battery = pump["battery"]
            if isinstance(battery, dict):
                result["battery"] = battery.get("percent")
            else:
                result["battery"] = battery

        # Basal rate
        if "extended" in pump and "BaseBasalRate" in pump["extended"]:
            result["basal_rate"] = pump["extended"]["BaseBasalRate"]

        return result if result else None

    def extract_phone_battery(
        self, devicestatus: list[dict[str, Any]]
    ) -> int | None:
        """Extract phone battery from device status."""
        if not devicestatus:
            return None

        status = devicestatus[0]

        # Try uploader battery
        if "uploader" in status and "battery" in status["uploader"]:
            return status["uploader"]["battery"]

        # Try uploaderBattery
        if "uploaderBattery" in status:
            return status["uploaderBattery"]

        return None

    def extract_temp_basal(
        self, devicestatus: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Extract temporary basal from device status."""
        if not devicestatus:
            return None

        status = devicestatus[0]

        # Try OpenAPS format
        if "openaps" in status:
            openaps = status["openaps"]
            if "enacted" in openaps:
                enacted = openaps["enacted"]
                if "rate" in enacted and "duration" in enacted:
                    return {
                        "rate": enacted["rate"],
                        "duration": enacted["duration"],
                        "timestamp": enacted.get("timestamp"),
                    }

        return None

    def extract_loop_status(
        self, devicestatus: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Extract loop status information."""
        if not devicestatus:
            return None

        status = devicestatus[0]

        # OpenAPS
        if "openaps" in status:
            return {
                "type": "OpenAPS",
                "device": status.get("device", ""),
                "timestamp": status.get("created_at"),
            }

        # Loop
        if "loop" in status:
            loop = status["loop"]
            return {
                "type": "Loop",
                "version": loop.get("version"),
                "device": status.get("device", ""),
                "timestamp": loop.get("timestamp"),
            }

        return None

    def calculate_ea1c(self, entries: list[dict[str, Any]]) -> float | None:
        """Calculate eA1c (estimated A1c) from glucose entries using GMI formula."""
        if not entries:
            return None

        # Extract glucose values
        glucose_values = []
        for entry in entries:
            if "sgv" in entry and entry["sgv"]:
                glucose_values.append(entry["sgv"])

        if not glucose_values:
            return None

        # Calculate average glucose
        avg_glucose = sum(glucose_values) / len(glucose_values)

        # GMI formula: eA1c(%) = 3.31 + 0.02392 × [average glucose in mg/dL]
        ea1c = 3.31 + (0.02392 * avg_glucose)

        return round(ea1c, 1)

    def calculate_time_in_range(
        self, entries: list[dict[str, Any]], low: int = 70, high: int = 180
    ) -> dict[str, float]:
        """Calculate time in range statistics."""
        if not entries:
            return {"in_range": 0, "below_range": 0, "above_range": 0}

        total = len(entries)
        in_range = 0
        below_range = 0
        above_range = 0

        for entry in entries:
            if "sgv" in entry and entry["sgv"]:
                value = entry["sgv"]
                if value < low:
                    below_range += 1
                elif value > high:
                    above_range += 1
                else:
                    in_range += 1

        return {
            "in_range": round((in_range / total) * 100, 1),
            "below_range": round((below_range / total) * 100, 1),
            "above_range": round((above_range / total) * 100, 1),
        }

    def extract_last_treatment(
        self, treatments: list[dict[str, Any]], event_type: str | None = None
    ) -> dict[str, Any] | None:
        """Extract last treatment of a specific type."""
        if not treatments:
            return None

        # Filter by event type if specified
        if event_type:
            filtered = [t for t in treatments if t.get("eventType") == event_type]
            if not filtered:
                return None
            treatment = filtered[0]
        else:
            treatment = treatments[0]

        return {
            "event_type": treatment.get("eventType"),
            "insulin": treatment.get("insulin"),
            "carbs": treatment.get("carbs"),
            "notes": treatment.get("notes"),
            "entered_by": treatment.get("enteredBy"),
            "created_at": treatment.get("created_at"),
        }
