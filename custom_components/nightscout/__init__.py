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
    CONF_ENABLE_DDNS,
    DOMAIN,
    STATISTICS_UPDATE_INTERVAL,
    UPDATE_INTERVAL,
)
from .diagnostics import NightscoutDiagnostics, DDNSManager

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

    # Create main coordinator (for real-time data)
    coordinator = NightscoutDataUpdateCoordinator(hass, api)

    # Create statistics coordinator (for statistical data - updates every 6 hours)
    statistics_coordinator = NightscoutStatisticsUpdateCoordinator(hass, api)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    await statistics_coordinator.async_config_entry_first_refresh()

    # Setup DDNS manager if enabled
    ddns_manager = None
    if entry.data.get(CONF_ENABLE_DDNS, False):
        ddns_manager = DDNSManager(session)
        # Schedule initial DDNS update
        hass.async_create_task(_async_update_ddns(hass, entry, ddns_manager))

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "statistics_coordinator": statistics_coordinator,
        "diagnostics": diagnostics,
        "ddns_manager": ddns_manager,
    }

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_ddns(
    hass: HomeAssistant,
    entry: ConfigEntry,
    ddns_manager: DDNSManager,
) -> None:
    """Update DDNS and save last update time."""
    from .const import (
        CONF_DDNS_SERVICE,
        CONF_DDNS_DOMAIN,
        CONF_DDNS_TOKEN,
        CONF_DDNS_UPDATE_URL,
        CONF_DDNS_LAST_UPDATE,
    )
    from datetime import datetime

    try:
        service = entry.data.get(CONF_DDNS_SERVICE)
        if service == "freedns":
            update_url = entry.data.get(CONF_DDNS_UPDATE_URL)
            if update_url:
                result = await ddns_manager.update_freedns(update_url)
                if result.get("success"):
                    _LOGGER.info("DDNS updated successfully via FreeDNS")
                    # Save last update time
                    new_data = {**entry.data, CONF_DDNS_LAST_UPDATE: datetime.now().isoformat()}
                    hass.config_entries.async_update_entry(entry, data=new_data)
        elif service == "duckdns":
            domain = entry.data.get(CONF_DDNS_DOMAIN)
            token = entry.data.get(CONF_DDNS_TOKEN)
            if domain and token:
                result = await ddns_manager.update_duckdns(domain, token)
                if result.get("success"):
                    _LOGGER.info("DDNS updated successfully via DuckDNS")
                    # Save last update time
                    new_data = {**entry.data, CONF_DDNS_LAST_UPDATE: datetime.now().isoformat()}
                    hass.config_entries.async_update_entry(entry, data=new_data)
    except Exception as err:
        _LOGGER.error("Failed to update DDNS: %s", err)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class NightscoutDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Nightscout real-time data."""

    def __init__(self, hass: HomeAssistant, api: NightscoutAPI) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_realtime",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        """Fetch real-time data from Nightscout."""
        try:
            # Fetch real-time data
            entries = await self.api.get_entries(count=1)
            devicestatus = await self.api.get_devicestatus(count=1)
            treatments = await self.api.get_treatments(count=10)

            return {
                "entries": entries,
                "devicestatus": devicestatus,
                "treatments": treatments,
            }
        except (aiohttp.ClientError, Exception) as err:
            raise UpdateFailed(f"Error communicating with Nightscout: {err}") from err


class NightscoutStatisticsUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Nightscout statistical data (updates every 6 hours)."""

    def __init__(self, hass: HomeAssistant, api: NightscoutAPI) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_statistics",
            update_interval=timedelta(seconds=STATISTICS_UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        """Fetch statistical data from Nightscout."""
        try:
            # Fetch entries for statistical calculations (24h, 7d, 30d, 90d)
            entries_24h = await self.api.get_entries_for_period(24)
            entries_7d = await self.api.get_entries_for_period(168)
            entries_30d = await self.api.get_entries_for_period(720)
            entries_90d = await self.api.get_entries_for_period(2160)

            return {
                "entries_24h": entries_24h,
                "entries_7d": entries_7d,
                "entries_30d": entries_30d,
                "entries_90d": entries_90d,
            }
        except (aiohttp.ClientError, Exception) as err:
            raise UpdateFailed(f"Error communicating with Nightscout: {err}") from err
