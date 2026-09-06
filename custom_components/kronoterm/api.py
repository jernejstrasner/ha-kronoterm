"""Async client for the Kronoterm local cloud-emulator API.

The emulator (https://github.com/jernejstrasner/kronoterm-local) impersonates the
Kronoterm cloud endpoint on the LAN and exposes a tiny HTTP API:

    GET  /api/health            -> {"ok": true, "module_connected": bool, "uid": str}
    GET  /api/registers         -> {"registers": {"<addr>": {"value": int, "ts": str}},
                                    "module_connected": bool, "uid": str}
    POST /api/write {addr, val} -> {"ok": true, ...}
"""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession, ClientTimeout

DEFAULT_TIMEOUT = ClientTimeout(total=10)


class KronotermError(Exception):
    """Base error for the Kronoterm API client."""


class KronotermConnectionError(KronotermError):
    """Raised when the emulator cannot be reached."""


class KronotermApiError(KronotermError):
    """Raised when the emulator returns an error response."""


class KronotermApi:
    """Minimal async client for the emulator HTTP API."""

    def __init__(self, session: ClientSession, host: str, port: int) -> None:
        """Initialize the client."""
        self._session = session
        self.host = host
        self.port = port
        self._base = f"http://{host}:{port}"

    async def _get(self, path: str) -> dict[str, Any]:
        """Perform a GET request and return the decoded JSON body."""
        try:
            async with self._session.get(
                f"{self._base}{path}", timeout=DEFAULT_TIMEOUT
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
        except (ClientError, asyncio.TimeoutError) as err:
            raise KronotermConnectionError(
                f"Cannot reach Kronoterm emulator at {self._base}: {err}"
            ) from err

    async def async_health(self) -> dict[str, Any]:
        """Return emulator health, including module connection state and UID."""
        return await self._get("/api/health")

    async def async_get_registers(self) -> dict[str, Any]:
        """Return the full register dump plus module state."""
        return await self._get("/api/registers")

    async def async_write_register(self, addr: int, value: int) -> None:
        """Write a raw register value via the emulator."""
        raw = value & 0xFFFF  # signed values are sent as two's complement
        try:
            async with self._session.post(
                f"{self._base}/api/write",
                json={"addr": addr, "value": raw},
                timeout=DEFAULT_TIMEOUT,
            ) as resp:
                resp.raise_for_status()
                body = await resp.json()
        except ClientResponseError as err:
            raise KronotermApiError(f"Write failed: HTTP {err.status}") from err
        except (ClientError, asyncio.TimeoutError) as err:
            raise KronotermConnectionError(
                f"Cannot reach Kronoterm emulator at {self._base}: {err}"
            ) from err
        if not body.get("ok"):
            raise KronotermApiError(f"Write rejected: {body}")
