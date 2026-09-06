"""Binary sensors for the Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    LOOPS,
    REG_COMPRESSOR_STATUS,
    REG_DEFROST_STATUS,
    REG_DHW_CIRCULATION_STATUS,
    REG_ERROR_WARNING,
    REG_MAIN_PUMP_STATUS,
)
from .coordinator import KronotermCoordinator
from .entity import KronotermEntity, register_valid


@dataclass(frozen=True, kw_only=True)
class KronotermBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a Kronoterm register-backed binary sensor."""

    addr: int = 0
    on_values: frozenset[int] = frozenset({1})


BINARY_SENSORS: tuple[KronotermBinarySensorDescription, ...] = (
    KronotermBinarySensorDescription(
        key="compressor_running",
        name="Compressor",
        addr=REG_COMPRESSOR_STATUS,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:hvac",
    ),
    KronotermBinarySensorDescription(
        key="defrost",
        name="Defrost",
        addr=REG_DEFROST_STATUS,
        icon="mdi:snowflake-melt",
    ),
    KronotermBinarySensorDescription(
        key="problem",
        name="Problem",
        addr=REG_ERROR_WARNING,
        on_values=frozenset({1, 2, 3}),
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    KronotermBinarySensorDescription(
        key="dhw_circulation",
        name="DHW circulation",
        addr=REG_DHW_CIRCULATION_STATUS,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pump",
    ),
    KronotermBinarySensorDescription(
        key="main_pump",
        name="Main circulation pump",
        addr=REG_MAIN_PUMP_STATUS,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pump",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kronoterm binary sensors from a config entry."""
    coordinator: KronotermCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = [
        KronotermBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    ]
    # Loop pumps, only for loops that report a real temperature.
    for n, regs in LOOPS.items():
        if register_valid(coordinator.data.registers, regs["temp"]):
            entities.append(
                KronotermBinarySensor(
                    coordinator,
                    KronotermBinarySensorDescription(
                        key=f"loop_{n}_pump",
                        name=f"Loop {n} pump",
                        addr=regs["pump"],
                        device_class=BinarySensorDeviceClass.RUNNING,
                        icon="mdi:pump",
                    ),
                )
            )
    entities.append(KronotermModuleConnectedSensor(coordinator))
    async_add_entities(entities)


class KronotermBinarySensor(KronotermEntity, BinarySensorEntity):
    """A register-backed Kronoterm binary sensor."""

    entity_description: KronotermBinarySensorDescription

    def __init__(
        self,
        coordinator: KronotermCoordinator,
        description: KronotermBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""
        value = self.raw(self.entity_description.addr)
        if value is None:
            return None
        return value in self.entity_description.on_values


class KronotermModuleConnectedSensor(KronotermEntity, BinarySensorEntity):
    """Reports whether the heat pump module is connected to the emulator."""

    _attr_name = "Module connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KronotermCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "module_connected")

    @property
    def is_on(self) -> bool:
        """Return the connection state."""
        return self.coordinator.data.module_connected
