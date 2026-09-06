"""Config flow for the Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KronotermApi, KronotermConnectionError
from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


class KronotermConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kronoterm Heat Pump (Local)."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: emulator host and port."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api = KronotermApi(
                async_get_clientsession(self.hass),
                user_input[CONF_HOST],
                user_input[CONF_PORT],
            )
            try:
                health = await api.async_health()
            except KronotermConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error validating emulator")
                errors["base"] = "unknown"
            else:
                uid = health.get("uid") or (
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                await self.async_set_unique_id(uid)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Kronoterm Heat Pump ({user_input[CONF_HOST]})",
                    data=user_input,
                )
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
