"""Climate entities (heating/cooling loops) for Kronoterm Heat Pump (Local)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_TENTHS, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    LOOP_MODE_NORMAL,
    LOOP_MODE_OFF,
    LOOP_MODE_SCHEDULE,
    LOOPS,
    REG_OPERATION_REGIME,
)
from .coordinator import KronotermCoordinator
from .entity import KronotermEntity, register_valid

HVAC_MODE_BY_LOOP_MODE = {
    LOOP_MODE_OFF: HVACMode.OFF,
    LOOP_MODE_NORMAL: HVACMode.HEAT_COOL,
    LOOP_MODE_SCHEDULE: HVACMode.AUTO,
}
LOOP_MODE_BY_HVAC_MODE = {v: k for k, v in HVAC_MODE_BY_LOOP_MODE.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kronoterm climate entities from a config entry."""
    coordinator: KronotermCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Only create climate entities for loops that report a real temperature.
    async_add_entities(
        KronotermLoopClimate(coordinator, n, regs)
        for n, regs in LOOPS.items()
        if register_valid(coordinator.data.registers, regs["temp"])
    )


class KronotermLoopClimate(KronotermEntity, ClimateEntity):
    """Climate entity for one heating/cooling loop."""

    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT_COOL, HVACMode.AUTO]
    _attr_precision = PRECISION_TENTHS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 10.0
    _attr_max_temp = 30.0
    _attr_target_temperature_step = 0.5
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(
        self, coordinator: KronotermCoordinator, loop: int, regs: dict[str, int]
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator, f"loop_{loop}_climate")
        self._loop = loop
        self._regs = regs
        self._attr_name = f"Loop {loop}"

    @property
    def current_temperature(self) -> float | None:
        """Return the current loop (room) temperature."""
        return self.scaled(self._regs["temp"], 0.1)

    @property
    def target_temperature(self) -> float | None:
        """Return the loop setpoint."""
        return self.scaled(self._regs["setpoint"], 0.1)

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current HVAC mode."""
        value = self.raw(self._regs["mode"])
        if value is None:
            return None
        return HVAC_MODE_BY_LOOP_MODE.get(value)

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action."""
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        pump = self.raw(self._regs["pump"])
        if not pump:
            return HVACAction.IDLE
        regime = self.raw(REG_OPERATION_REGIME)
        if regime == 1:
            return HVACAction.HEATING
        if regime == 0:
            return HVACAction.COOLING
        return HVACAction.IDLE

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set a new loop setpoint."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self._async_write(self._regs["setpoint"], round(temperature * 10))

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set a new HVAC mode (off / normal / schedule)."""
        await self._async_write(self._regs["mode"], LOOP_MODE_BY_HVAC_MODE[hvac_mode])
