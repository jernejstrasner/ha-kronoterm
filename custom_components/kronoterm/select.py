"""Selects for the Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MODE_SWITCH,
    OPERATION_PROGRAM_SELECT,
    REG_MODE_SWITCH,
    REG_OPERATION_PROGRAM_SELECT,
)
from .coordinator import KronotermCoordinator
from .entity import KronotermEntity

OPTIONS = list(OPERATION_PROGRAM_SELECT.values())
VALUE_BY_OPTION = {v: k for k, v in OPERATION_PROGRAM_SELECT.items()}

MODE_OPTIONS = list(MODE_SWITCH.values())
MODE_VALUE_BY_OPTION = {v: k for k, v in MODE_SWITCH.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kronoterm selects from a config entry."""
    coordinator: KronotermCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            KronotermOperationProgramSelect(coordinator),
            KronotermModeSwitchSelect(coordinator),
        ]
    )


class KronotermOperationProgramSelect(KronotermEntity, SelectEntity):
    """Select the global operation program (normal / eco / comfort)."""

    _attr_name = "Operation program select"
    _attr_icon = "mdi:tune"
    _attr_options = OPTIONS

    def __init__(self, coordinator: KronotermCoordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "operation_program_select")

    @property
    def current_option(self) -> str | None:
        """Return the current operation program."""
        value = self.raw(REG_OPERATION_PROGRAM_SELECT)
        if value is None:
            return None
        return OPERATION_PROGRAM_SELECT.get(value)

    async def async_select_option(self, option: str) -> None:
        """Set the operation program."""
        await self._async_write(REG_OPERATION_PROGRAM_SELECT, VALUE_BY_OPTION[option])


class KronotermModeSwitchSelect(KronotermEntity, SelectEntity):
    """Select the heating/cooling mode, as on the Kronoterm dashboard."""

    _attr_name = "Mode switch"
    _attr_icon = "mdi:swap-horizontal"
    _attr_options = MODE_OPTIONS

    def __init__(self, coordinator: KronotermCoordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "mode_switch")

    @property
    def current_option(self) -> str | None:
        """Return the current mode."""
        value = self.raw(REG_MODE_SWITCH)
        if value is None:
            return None
        return MODE_SWITCH.get(value)

    async def async_select_option(self, option: str) -> None:
        """Set the heating/cooling mode."""
        await self._async_write(REG_MODE_SWITCH, MODE_VALUE_BY_OPTION[option])
