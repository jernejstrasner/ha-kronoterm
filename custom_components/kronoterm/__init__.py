"""The Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KronotermApi
from .const import DEFAULT_PORT, DOMAIN
from .coordinator import KronotermCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Kronoterm Heat Pump (Local) from a config entry."""
    api = KronotermApi(
        async_get_clientsession(hass),
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
    )
    uid = entry.unique_id or f"{entry.data[CONF_HOST]}:{entry.data[CONF_PORT]}"
    coordinator = KronotermCoordinator(hass, api, uid)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
