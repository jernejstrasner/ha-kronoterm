"""Sensors for the Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    ERROR_WARNING,
    LOOPS,
    OPERATION_PROGRAM,
    OPERATION_REGIME,
    REG_CAPACITY,
    REG_COMPRESSOR_INLET_TEMP,
    REG_COMPRESSOR_MINUTES_DAILY,
    REG_COMPRESSOR_OUTLET_TEMP,
    REG_COP,
    REG_DHW_TEMP,
    REG_ELECTRICAL_ENERGY,
    REG_ERROR_FLAGS,
    REG_ERROR_WARNING,
    REG_EXPERIMENTAL,
    REG_HEATING_ENERGY,
    REG_HOURS_COMPRESSOR_DHW,
    REG_HOURS_COMPRESSOR_HEATING,
    REG_HOURS_COOLING,
    REG_HP_INLET_TEMP,
    REG_HP_LOAD,
    REG_HP_OUTLET_TEMP,
    REG_OPERATION_PROGRAM,
    REG_OPERATION_REGIME,
    REG_OUTSIDE_TEMP,
    REG_POWER,
    REG_PRESSURE,
    REG_SCOP,
    REG_WORKING_FUNCTION,
    WORKING_FUNCTION,
)
from .coordinator import KronotermCoordinator
from .entity import KronotermEntity, register_valid


@dataclass(frozen=True, kw_only=True)
class KronotermSensorDescription(SensorEntityDescription):
    """Describes a Kronoterm register-backed sensor."""

    addr: int
    scale: float = 1.0
    signed: bool = False
    value_map: dict[int, str] | None = None


SENSORS: tuple[KronotermSensorDescription, ...] = (
    # -- temperatures
    KronotermSensorDescription(
        key="outside_temperature",
        name="Outside temperature",
        addr=REG_OUTSIDE_TEMP,
        scale=0.1,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        signed=True,
    ),
    KronotermSensorDescription(
        key="dhw_temperature",
        name="DHW temperature",
        addr=REG_DHW_TEMP,
        scale=0.1,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        signed=True,
    ),
    KronotermSensorDescription(
        key="hp_inlet_temperature",
        name="Heat pump inlet temperature",
        addr=REG_HP_INLET_TEMP,
        scale=0.1,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        signed=True,
        entity_registry_enabled_default=False,
    ),
    KronotermSensorDescription(
        key="hp_outlet_temperature",
        name="Heat pump outlet temperature",
        addr=REG_HP_OUTLET_TEMP,
        scale=0.1,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        signed=True,
    ),
    KronotermSensorDescription(
        key="compressor_inlet_temperature",
        name="Compressor inlet temperature",
        addr=REG_COMPRESSOR_INLET_TEMP,
        scale=0.1,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        signed=True,
        entity_registry_enabled_default=False,
    ),
    KronotermSensorDescription(
        key="compressor_outlet_temperature",
        name="Compressor outlet temperature",
        addr=REG_COMPRESSOR_OUTLET_TEMP,
        scale=0.1,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        signed=True,
        entity_registry_enabled_default=False,
    ),
    # -- performance
    KronotermSensorDescription(
        key="power",
        name="Electrical power",
        addr=REG_POWER,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    KronotermSensorDescription(
        key="capacity",
        name="Thermal capacity",
        addr=REG_CAPACITY,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    KronotermSensorDescription(
        key="cop",
        name="COP",
        addr=REG_COP,
        scale=0.01,
        icon="mdi:heat-pump-outline",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    KronotermSensorDescription(
        key="scop",
        name="SCOP",
        addr=REG_SCOP,
        scale=0.01,
        icon="mdi:heat-pump-outline",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    KronotermSensorDescription(
        key="electrical_energy",
        name="Electrical energy",
        addr=REG_ELECTRICAL_ENERGY,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    KronotermSensorDescription(
        key="heating_energy",
        name="Thermal energy",
        addr=REG_HEATING_ENERGY,
        scale=0.1,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    KronotermSensorDescription(
        key="pressure",
        name="System pressure",
        addr=REG_PRESSURE,
        scale=0.1,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    KronotermSensorDescription(
        key="hp_load",
        name="Heat pump load",
        addr=REG_HP_LOAD,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    # -- status enums
    KronotermSensorDescription(
        key="working_function",
        name="Working function",
        addr=REG_WORKING_FUNCTION,
        device_class=SensorDeviceClass.ENUM,
        options=list(WORKING_FUNCTION.values()) + ["unknown"],
        value_map=WORKING_FUNCTION,
        icon="mdi:cog",
    ),
    KronotermSensorDescription(
        key="operation_regime",
        name="Operation regime",
        addr=REG_OPERATION_REGIME,
        device_class=SensorDeviceClass.ENUM,
        options=list(OPERATION_REGIME.values()) + ["unknown"],
        value_map=OPERATION_REGIME,
        icon="mdi:swap-horizontal",
    ),
    KronotermSensorDescription(
        key="operation_program",
        name="Operation program",
        addr=REG_OPERATION_PROGRAM,
        device_class=SensorDeviceClass.ENUM,
        options=list(OPERATION_PROGRAM.values()) + ["unknown"],
        value_map=OPERATION_PROGRAM,
        icon="mdi:calendar-clock",
    ),
    KronotermSensorDescription(
        key="error_warning",
        name="Error status",
        addr=REG_ERROR_WARNING,
        device_class=SensorDeviceClass.ENUM,
        options=list(ERROR_WARNING.values()) + ["unknown"],
        value_map=ERROR_WARNING,
        icon="mdi:alert-circle-outline",
    ),
    # -- runtime counters (diagnostic)
    KronotermSensorDescription(
        key="hours_compressor_heating",
        name="Compressor hours heating",
        addr=REG_HOURS_COMPRESSOR_HEATING,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KronotermSensorDescription(
        key="hours_compressor_dhw",
        name="Compressor hours DHW",
        addr=REG_HOURS_COMPRESSOR_DHW,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KronotermSensorDescription(
        key="hours_cooling",
        name="Hours cooling",
        addr=REG_HOURS_COOLING,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KronotermSensorDescription(
        key="compressor_minutes_today",
        name="Compressor minutes today",
        addr=REG_COMPRESSOR_MINUTES_DAILY,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KronotermSensorDescription(
        key="error_flags",
        name="Error flags",
        addr=REG_ERROR_FLAGS,
        icon="mdi:flag",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)

# Undocumented registers, exposed disabled-by-default for exploration.
EXPERIMENTAL_SENSORS: tuple[KronotermSensorDescription, ...] = tuple(
    KronotermSensorDescription(
        key=key,
        name=f"Experimental {key.removeprefix('reg_')}",
        addr=addr,
        scale=scale,
        native_unit_of_measurement=unit,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    )
    for addr, (key, scale, unit) in REG_EXPERIMENTAL.items()
)


def _loop_sensors() -> tuple[KronotermSensorDescription, ...]:
    """Build temperature sensor descriptions for each heating loop."""
    return tuple(
        KronotermSensorDescription(
            key=f"loop_{n}_temperature",
            name=f"Loop {n} temperature",
            addr=regs["temp"],
            scale=0.1,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            signed=True,
        )
        for n, regs in LOOPS.items()
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kronoterm sensors from a config entry."""
    coordinator: KronotermCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[KronotermSensor] = [
        KronotermSensor(coordinator, description)
        for description in (*SENSORS, *EXPERIMENTAL_SENSORS)
    ]
    # Only create loop sensors for loops that actually report a temperature.
    for description in _loop_sensors():
        if register_valid(coordinator.data.registers, description.addr):
            entities.append(KronotermSensor(coordinator, description))
    async_add_entities(entities)


class KronotermSensor(KronotermEntity, SensorEntity):
    """A register-backed Kronoterm sensor."""

    entity_description: KronotermSensorDescription

    def __init__(
        self,
        coordinator: KronotermCoordinator,
        description: KronotermSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | int | str | None:
        """Return the sensor value."""
        value = self.raw(self.entity_description.addr, signed=self.entity_description.signed)
        if value is None:
            return None
        if self.entity_description.value_map is not None:
            return self.entity_description.value_map.get(value, "unknown")
        return value * self.entity_description.scale
