"""Switches for the Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    REG_DHW_CIRCULATION_PUMP,
    REG_SYSTEM_ON,
    REG_THERMAL_DISINFECTION,
    REG_VACATION_MODE,
)
from .coordinator import KronotermCoordinator
from .entity import KronotermEntity


@dataclass(frozen=True, kw_only=True)
class KronotermSwitchDescription(SwitchEntityDescription):
    """Describes a Kronoterm register-backed switch."""

    addr: int


SWITCHES: tuple[KronotermSwitchDescription, ...] = (
    KronotermSwitchDescription(
        key="system_on",
        name="System",
        addr=REG_SYSTEM_ON,
        icon="mdi:power",
    ),
    KronotermSwitchDescription(
        key="vacation_mode",
        name="Vacation mode",
        addr=REG_VACATION_MODE,
        icon="mdi:beach",
    ),
    KronotermSwitchDescription(
        key="thermal_disinfection",
        name="Thermal disinfection",
        addr=REG_THERMAL_DISINFECTION,
        icon="mdi:bacteria-outline",
    ),
    KronotermSwitchDescription(
        key="dhw_circulation_pump",
        name="DHW circulation pump",
        addr=REG_DHW_CIRCULATION_PUMP,
        icon="mdi:pump",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kronoterm switches from a config entry."""
    coordinator: KronotermCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        KronotermSwitch(coordinator, description) for description in SWITCHES
    )


class KronotermSwitch(KronotermEntity, SwitchEntity):
    """A register-backed Kronoterm switch."""

    entity_description: KronotermSwitchDescription

    def __init__(
        self,
        coordinator: KronotermCoordinator,
        description: KronotermSwitchDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return the switch state."""
        value = self.raw(self.entity_description.addr)
        if value is None:
            return None
        return value == 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._async_write(self.entity_description.addr, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._async_write(self.entity_description.addr, 0)
