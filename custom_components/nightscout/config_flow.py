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
    CONF_DOMAIN_EXPIRY,
    CONF_ENABLE_DDNS,
    CONF_GLUCOSE_UNIT,
    CONF_TARGET_MAX,
    CONF_TARGET_MIN,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Optional(CONF_API_KEY): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api = NightscoutAPI(session, data[CONF_URL], data.get(CONF_API_KEY))

    if not await api.test_connection():
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {"title": "Nightscout"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nightscout Extended."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Nightscout Extended."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        
        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_GLUCOSE_UNIT,
                    default=options.get(CONF_GLUCOSE_UNIT, "mg/dL"),
                ): vol.In(["mg/dL", "mmol/L"]),
                vol.Optional(
                    CONF_TARGET_MIN,
                    default=options.get(CONF_TARGET_MIN, 70),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_TARGET_MAX,
                    default=options.get(CONF_TARGET_MAX, 180),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_ENABLE_DDNS,
                    default=options.get(CONF_ENABLE_DDNS, False),
                ): bool,
            }
        )

        # If DDNS is enabled, add DDNS fields
        if options.get(CONF_ENABLE_DDNS, False) or (
            user_input and user_input.get(CONF_ENABLE_DDNS, False)
        ):
            data_schema = data_schema.extend(
                {
                    vol.Optional(
                        CONF_DDNS_SERVICE,
                        default=options.get(CONF_DDNS_SERVICE, "freedns"),
                    ): vol.In(["freedns", "duckdns"]),
                    vol.Optional(
                        CONF_DDNS_DOMAIN,
                        default=options.get(CONF_DDNS_DOMAIN, ""),
                    ): str,
                    vol.Optional(
                        CONF_DDNS_TOKEN,
                        default=options.get(CONF_DDNS_TOKEN, ""),
                    ): str,
                    vol.Optional(
                        CONF_DDNS_UPDATE_URL,
                        default=options.get(CONF_DDNS_UPDATE_URL, ""),
                    ): str,
                    vol.Optional(
                        CONF_DOMAIN_EXPIRY,
                        default=options.get(CONF_DOMAIN_EXPIRY, ""),
                    ): str,
                }
            )

        return self.async_show_form(step_id="init", data_schema=data_schema)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
