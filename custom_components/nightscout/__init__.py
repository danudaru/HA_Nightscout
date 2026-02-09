"""The Nightscout Extended integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NightscoutAPI
from .const import (
    CONF_API_KEY,
    CONF_URL,
    DOMAIN,
    STATISTICS_UPDATE_INTERVAL,
    UPDATE_INTERVAL,
)
from .diagnostics import NightscoutDiagnostics

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nightscout Extended from a config entry."""
    url = entry.data[CONF_URL]
    api_key = entry.data.get(CONF_API_KEY)

    session = async_get_clientsession(hass)
    api = NightscoutAPI(session, url, api_key)

    # Test connection
    if not await api.test_connection():
        _LOGGER.error("Failed to connect to Nightscout at %s", url)
        return False

    # Create diagnostics
    diagnostics = NightscoutDiagnostics(api, url)

    # Create coordinator
    coordinator = NightscoutDataUpdateCoordinator(hass, api)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "diagnostics": diagnostics,
    }

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class NightscoutDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Nightscout data."""

    def __init__(self, hass: HomeAssistant, api: NightscoutAPI) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        """Fetch data from Nightscout."""
        try:
            # Fetch all data in parallel
            entries = await self.api.get_entries(count=1)
            devicestatus = await self.api.get_devicestatus(count=1)
            treatments = await self.api.get_treatments(count=10)
            
            # Fetch entries for eA1c calculations
            entries_24h = await self.api.get_entries_for_period(24)
            entries_7d = await self.api.get_entries_for_period(168)
            entries_30d = await self.api.get_entries_for_period(720)
            entries_90d = await self.api.get_entries_for_period(2160)

            return {
                "entries": entries,
                "devicestatus": devicestatus,
                "treatments": treatments,
                "entries_24h": entries_24h,
                "entries_7d": entries_7d,
                "entries_30d": entries_30d,
                "entries_90d": entries_90d,
            }
        except (aiohttp.ClientError, Exception) as err:
            raise UpdateFailed(f"Error communicating with Nightscout: {err}") from err
