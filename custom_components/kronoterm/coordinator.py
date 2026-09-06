"""Data update coordinator for the Kronoterm Heat Pump (Local) integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import KronotermApi, KronotermError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class KronotermData:
    """Snapshot of the emulator state."""

    registers: dict[int, int] = field(default_factory=dict)
    module_connected: bool = False


class KronotermCoordinator(DataUpdateCoordinator[KronotermData]):
    """Polls the emulator API and dispatches updates to entities."""

    def __init__(self, hass: HomeAssistant, api: KronotermApi, uid: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self.uid = uid

    async def _async_update_data(self) -> KronotermData:
        """Fetch the full register dump from the emulator."""
        try:
            payload = await self.api.async_get_registers()
        except KronotermError as err:
            raise UpdateFailed(str(err)) from err
        registers = {
            int(addr): int(entry["value"])
            for addr, entry in payload.get("registers", {}).items()
        }
        return KronotermData(
            registers=registers,
            module_connected=bool(payload.get("module_connected")),
        )
