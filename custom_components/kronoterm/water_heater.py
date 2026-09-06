"""Water heater entity (domestic hot water) for Kronoterm Heat Pump (Local)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_TENTHS, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    DHW_MODE,
    REG_DHW_OPERATION_MODE,
    REG_DHW_SETPOINT,
    REG_DHW_TEMP,
)
from .coordinator import KronotermCoordinator
from .entity import KronotermEntity

OPERATION_LIST = list(DHW_MODE.values())
DHW_MODE_BY_OPERATION = {v: k for k, v in DHW_MODE.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Kronoterm water heater from a config entry."""
    coordinator: KronotermCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KronotermWaterHeater(coordinator)])


class KronotermWaterHeater(KronotermEntity, WaterHeaterEntity):
    """Domestic hot water entity."""

    _attr_name = "Domestic hot water"
    _attr_icon = "mdi:water-boiler"
    _attr_operation_list = OPERATION_LIST
    _attr_precision = PRECISION_TENTHS
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 10.0
    _attr_max_temp = 65.0

    def __init__(self, coordinator: KronotermCoordinator) -> None:
        """Initialize the water heater."""
        super().__init__(coordinator, "dhw")

    @property
    def current_temperature(self) -> float | None:
        """Return the current DHW temperature."""
        return self.scaled(REG_DHW_TEMP, 0.1)

    @property
    def target_temperature(self) -> float | None:
        """Return the DHW setpoint."""
        return self.scaled(REG_DHW_SETPOINT, 0.1)

    @property
    def current_operation(self) -> str | None:
        """Return the current DHW operation mode."""
        value = self.raw(REG_DHW_OPERATION_MODE)
        if value is None:
            return None
        return DHW_MODE.get(value)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set a new DHW setpoint."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self._async_write(REG_DHW_SETPOINT, round(temperature * 10))

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set the DHW operation mode (off / normal / schedule)."""
        await self._async_write(
            REG_DHW_OPERATION_MODE, DHW_MODE_BY_OPERATION[operation_mode]
        )
