"""Numbers for the Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    LOOP_CURVE_COLD,
    LOOP_CURVE_WARM,
    LOOP_ECO_OFFSET,
    LOOP_COMFORT_OFFSET,
    LOOPS,
    REG_DHW_COMFORT_OFFSET,
    REG_DHW_ECO_OFFSET,
    REG_SYSTEM_TEMP_CORRECTION,
)
from .coordinator import KronotermCoordinator
from .entity import KronotermEntity, register_valid


@dataclass(frozen=True, kw_only=True)
class KronotermNumberDescription(NumberEntityDescription):
    """Describes a Kronoterm register-backed number entity."""

    addr: int
    scale: float = 1.0
    signed: bool = False
    min_value: float = 0.0
    max_value: float = 100.0
    step: float = 1.0


NUMBERS: tuple[KronotermNumberDescription, ...] = (
    KronotermNumberDescription(
        key="system_temperature_correction",
        name="System temperature correction",
        addr=REG_SYSTEM_TEMP_CORRECTION,
        signed=True,
        min_value=-5.0,
        max_value=5.0,
        step=1.0,
        icon="mdi:thermometer-plus",
    ),
    KronotermNumberDescription(
        key="dhw_eco_offset",
        name="DHW ECO offset",
        addr=REG_DHW_ECO_OFFSET,
        scale=0.1,
        signed=True,
        min_value=-10.0,
        max_value=10.0,
        step=0.5,
        icon="mdi:leaf",
    ),
    KronotermNumberDescription(
        key="dhw_comfort_offset",
        name="DHW comfort offset",
        addr=REG_DHW_COMFORT_OFFSET,
        scale=0.1,
        signed=True,
        min_value=-10.0,
        max_value=10.0,
        step=0.5,
        icon="mdi:sofa",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kronoterm numbers from a config entry."""
    coordinator: KronotermCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [KronotermNumber(coordinator, d) for d in NUMBERS]
    # Per-loop settings, only for loops that report a real temperature.
    for n, regs in LOOPS.items():
        if not register_valid(coordinator.data.registers, regs["temp"]):
            continue
        entities += [
            KronotermNumber(
                coordinator,
                KronotermNumberDescription(
                    key=f"loop_{n}_curve_cold_point",
                    name=f"Loop {n} curve cold point",
                    addr=LOOP_CURVE_COLD[n],
                    scale=0.1,
                    min_value=10.0,
                    max_value=60.0,
                    step=0.5,
                    icon="mdi:chart-bell-curve",
                ),
            ),
            KronotermNumber(
                coordinator,
                KronotermNumberDescription(
                    key=f"loop_{n}_curve_warm_point",
                    name=f"Loop {n} curve warm point",
                    addr=LOOP_CURVE_WARM[n],
                    scale=0.1,
                    min_value=10.0,
                    max_value=60.0,
                    step=0.5,
                    icon="mdi:chart-bell-curve",
                ),
            ),
            KronotermNumber(
                coordinator,
                KronotermNumberDescription(
                    key=f"loop_{n}_eco_offset",
                    name=f"Loop {n} ECO offset",
                    addr=LOOP_ECO_OFFSET[n],
                    scale=0.1,
                    signed=True,
                    min_value=-10.0,
                    max_value=10.0,
                    step=0.5,
                    icon="mdi:leaf",
                ),
            ),
            KronotermNumber(
                coordinator,
                KronotermNumberDescription(
                    key=f"loop_{n}_comfort_offset",
                    name=f"Loop {n} comfort offset",
                    addr=LOOP_COMFORT_OFFSET[n],
                    scale=0.1,
                    signed=True,
                    min_value=-10.0,
                    max_value=10.0,
                    step=0.5,
                    icon="mdi:sofa",
                ),
            ),
        ]
    async_add_entities(entities)


class KronotermNumber(KronotermEntity, NumberEntity):
    """A register-backed Kronoterm number entity."""

    _attr_mode = NumberMode.BOX
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_entity_category = EntityCategory.CONFIG

    entity_description: KronotermNumberDescription

    def __init__(
        self, coordinator: KronotermCoordinator, description: KronotermNumberDescription
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_native_min_value = description.min_value
        self._attr_native_max_value = description.max_value
        self._attr_native_step = description.step

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.scaled(
            self.entity_description.addr,
            self.entity_description.scale,
            signed=self.entity_description.signed,
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set a new value (signed values sent as two's complement)."""
        await self._async_write(
            self.entity_description.addr, round(value / self.entity_description.scale)
        )
