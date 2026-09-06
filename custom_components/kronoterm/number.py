"""Numbers for the Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, REG_SYSTEM_TEMP_CORRECTION
from .coordinator import KronotermCoordinator
from .entity import KronotermEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kronoterm numbers from a config entry."""
    coordinator: KronotermCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KronotermTempCorrectionNumber(coordinator)])


class KronotermTempCorrectionNumber(KronotermEntity, NumberEntity):
    """System temperature correction (-5..+5 °C, signed register)."""

    _attr_name = "System temperature correction"
    _attr_icon = "mdi:thermometer-plus"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_min_value = -5.0
    _attr_native_max_value = 5.0
    _attr_native_step = 1.0
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: KronotermCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator, "system_temperature_correction")

    @property
    def native_value(self) -> float | None:
        """Return the current correction."""
        value = self.raw(REG_SYSTEM_TEMP_CORRECTION)
        return None if value is None else float(value)

    async def async_set_native_value(self, value: float) -> None:
        """Set the correction (sent as two's complement when negative)."""
        await self._async_write(REG_SYSTEM_TEMP_CORRECTION, int(value))
