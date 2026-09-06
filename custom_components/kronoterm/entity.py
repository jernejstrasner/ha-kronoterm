"""Base entity for the Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENTINEL_UNSET
from .coordinator import KronotermCoordinator


def to_signed(value: int) -> int:
    """Interpret a raw 16-bit register as a signed integer."""
    return value - 0x10000 if value >= 0x8000 else value


def register_valid(registers: dict[int, int], addr: int) -> bool:
    """Return True if a register holds a real value (not a sentinel)."""
    value = registers.get(addr)
    if value is None:
        return False
    signed = to_signed(value)
    # "No sensor" reads as ~-60.0 °C (-600/-599 depending on unit), "unset" is 0x3FFF.
    return signed > -500 and signed != SENTINEL_UNSET


class KronotermEntity(CoordinatorEntity[KronotermCoordinator]):
    """Common base for all Kronoterm entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: KronotermCoordinator, key: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.uid}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.uid)},
            manufacturer="Kronoterm",
            model="TERMOTRONIC 3000",
            name="Kronoterm Heat Pump",
            serial_number=coordinator.uid,
            configuration_url=f"http://{coordinator.api.host}:{coordinator.api.port}/api/health",
        )

    def raw(self, addr: int, signed: bool = True) -> int | None:
        """Return the raw register value, or None if unknown/invalid.

        Temperature-like registers are signed (two's complement); counters
        and power registers are unsigned 16-bit.
        """
        value = self.coordinator.data.registers.get(addr)
        if value is None:
            return None
        if signed:
            value = to_signed(value)
            if value <= -500:  # "no sensor" sentinel (~-60.0 °C)
                return None
        if value == SENTINEL_UNSET:
            return None
        return value

    def scaled(self, addr: int, scale: float, signed: bool = True) -> float | None:
        """Return the scaled register value, or None if unknown/invalid."""
        value = self.raw(addr, signed=signed)
        return None if value is None else value * scale

    async def _async_write(self, addr: int, value: int) -> None:
        """Write a register and request a refresh."""
        await self.coordinator.api.async_write_register(addr, value)
        await self.coordinator.async_request_refresh()
