"""Config flow for Nightscout Extended integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NightscoutAPI
from .const import (
    CONF_API_KEY,
    CONF_DDNS_DOMAIN,
    CONF_DDNS_SERVICE,
    CONF_DDNS_TOKEN,
    CONF_DDNS_UPDATE_URL,
    CONF_ENABLE_DDNS,
    CONF_GLUCOSE_UNIT,
    CONF_TARGET_MAX,
    CONF_TARGET_MIN,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def get_step_1_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Get step 1 schema (URL, API key, glucose unit)."""
    if defaults is None:
        defaults = {}
    
    return vol.Schema(
        {
            vol.Required(CONF_URL, default=defaults.get(CONF_URL, "")): str,
            vol.Optional(CONF_API_KEY, default=defaults.get(CONF_API_KEY, "")): str,
            vol.Required(
                CONF_GLUCOSE_UNIT,
                default=defaults.get(CONF_GLUCOSE_UNIT, "mg/dL"),
            ): vol.In(["mg/dL", "mmol/L"]),
        }
    )


def get_step_2_schema(glucose_unit: str, defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Get step 2 schema (target range and DDNS) with unit-specific defaults."""
    if defaults is None:
        defaults = {}
    
    # Set defaults based on glucose unit
    if glucose_unit == "mmol/L":
        default_min = defaults.get(CONF_TARGET_MIN, 3.9)
        default_max = defaults.get(CONF_TARGET_MAX, 10.0)
    else:  # mg/dL
        default_min = defaults.get(CONF_TARGET_MIN, 70)
        default_max = defaults.get(CONF_TARGET_MAX, 180)
    
    return vol.Schema(
        {
            vol.Required(
                CONF_TARGET_MIN,
                default=default_min,
            ): vol.Coerce(float),
            vol.Required(
                CONF_TARGET_MAX,
                default=default_max,
            ): vol.Coerce(float),
            vol.Optional(
                CONF_ENABLE_DDNS,
                default=defaults.get(CONF_ENABLE_DDNS, False),
            ): bool,
            vol.Optional(
                CONF_DDNS_SERVICE,
                default=defaults.get(CONF_DDNS_SERVICE, "freedns"),
            ): vol.In(["freedns", "duckdns"]),
            vol.Optional(
                CONF_DDNS_DOMAIN,
                default=defaults.get(CONF_DDNS_DOMAIN, ""),
            ): str,
            vol.Optional(
                CONF_DDNS_TOKEN,
                default=defaults.get(CONF_DDNS_TOKEN, ""),
            ): str,
            vol.Optional(
                CONF_DDNS_UPDATE_URL,
                default=defaults.get(CONF_DDNS_UPDATE_URL, ""),
            ): str,
        }
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api = NightscoutAPI(session, data[CONF_URL], data.get(CONF_API_KEY))

    if not await api.test_connection():
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {"title": "Nightscout Extended"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nightscout Extended."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._data: dict[str, Any] = {}

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step (URL, API key, glucose unit)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                # Save data from step 1
                self._data.update(user_input)
                # Move to step 2
                return await self.async_step_preferences()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", 
            data_schema=get_step_1_schema(self._data),
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/danudaru/HA_Nightscout"
            }
        )

    async def async_step_preferences(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle preferences step (target range and DDNS)."""
        if user_input is not None:
            # Combine all data
            self._data.update(user_input)
            return self.async_create_entry(title="Nightscout Extended", data=self._data)

        # Get glucose unit from step 1
        glucose_unit = self._data.get(CONF_GLUCOSE_UNIT, "mg/dL")
        
        return self.async_show_form(
            step_id="preferences",
            data_schema=get_step_2_schema(glucose_unit, self._data),
            description_placeholders={
                "glucose_unit": glucose_unit,
            }
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Nightscout Extended."""

    def __init__(self) -> None:
        """Initialize options flow."""
        self._data: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - step 1 (URL, API key, glucose unit)."""
        if user_input is not None:
            # Check if glucose unit changed
            old_unit = self.config_entry.data.get(CONF_GLUCOSE_UNIT, "mg/dL")
            new_unit = user_input.get(CONF_GLUCOSE_UNIT, "mg/dL")
            
            # Save step 1 data
            self._data.update(user_input)
            
            # If unit changed, convert existing target values
            if old_unit != new_unit:
                old_min = self.config_entry.data.get(CONF_TARGET_MIN, 70 if old_unit == "mg/dL" else 3.9)
                old_max = self.config_entry.data.get(CONF_TARGET_MAX, 180 if old_unit == "mg/dL" else 10.0)
                
                if new_unit == "mmol/L" and old_unit == "mg/dL":
                    # Convert mg/dL to mmol/L
                    self._data[CONF_TARGET_MIN] = round(old_min / 18.0, 1)
                    self._data[CONF_TARGET_MAX] = round(old_max / 18.0, 1)
                elif new_unit == "mg/dL" and old_unit == "mmol/L":
                    # Convert mmol/L to mg/dL
                    self._data[CONF_TARGET_MIN] = round(old_min * 18.0, 0)
                    self._data[CONF_TARGET_MAX] = round(old_max * 18.0, 0)
            
            # Move to step 2
            return await self.async_step_preferences()

        # Get current config
        current_config = self.config_entry.data
        
        return self.async_show_form(
            step_id="init", 
            data_schema=get_step_1_schema(current_config),
            description_placeholders={
                "docs_url": "https://github.com/danudaru/HA_Nightscout"
            }
        )

    async def async_step_preferences(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage preferences (target range and DDNS)."""
        if user_input is not None:
            # Combine all data
            self._data.update(user_input)
            
            # Update config entry data
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=self._data
            )
            return self.async_create_entry(title="", data={})

        # Get glucose unit from step 1 or existing config
        glucose_unit = self._data.get(CONF_GLUCOSE_UNIT) or self.config_entry.data.get(CONF_GLUCOSE_UNIT, "mg/dL")
        
        # Merge current config with step 1 data
        current_config = {**self.config_entry.data, **self._data}
        
        return self.async_show_form(
            step_id="preferences",
            data_schema=get_step_2_schema(glucose_unit, current_config),
            description_placeholders={
                "glucose_unit": glucose_unit,
            }
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
