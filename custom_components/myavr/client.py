"""Modbus TCP client wrapper for the MyAVR ATS controller."""

from __future__ import annotations

import asyncio
import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import READ_BLOCKS

_LOGGER = logging.getLogger(__name__)


class MyAVRError(Exception):
    """Base error for MyAVR communication."""


class MyAVRConnectionError(MyAVRError):
    """Raised when the controller cannot be reached."""


class MyAVRClient:
    """Thin async wrapper around pymodbus for the MyAVR controller.

    The controller uses the FULL register number as the Modbus PDU address
    (30001 == address 30001), which is non-standard but verified on hardware.
    """

    def __init__(self, host: str, port: int, device_id: int) -> None:
        """Initialize the client."""
        self._host = host
        self._port = port
        self._device_id = device_id
        self._client = AsyncModbusTcpClient(host, port=port, timeout=5)
        self._lock = asyncio.Lock()

    async def async_connect(self) -> None:
        """Ensure the TCP connection is up."""
        if self._client.connected:
            return
        connected = await self._client.connect()
        if not connected:
            raise MyAVRConnectionError(
                f"Cannot connect to MyAVR controller at {self._host}:{self._port}"
            )

    async def async_close(self) -> None:
        """Close the connection."""
        self._client.close()

    async def async_read_all(self) -> dict[int, int]:
        """Read all input register blocks, return {register_number: value}."""
        result: dict[int, int] = {}
        async with self._lock:
            await self.async_connect()
            for start, count in READ_BLOCKS:
                try:
                    rr = await self._client.read_input_registers(
                        start, count=count, device_id=self._device_id
                    )
                except ModbusException as err:
                    raise MyAVRConnectionError(f"Modbus read failed: {err}") from err
                if rr.isError():
                    raise MyAVRConnectionError(
                        f"Modbus exception reading block {start}+{count}: {rr}"
                    )
                for offset, value in enumerate(rr.registers):
                    result[start + offset] = value
        return result

    async def async_write_command(self, register: int) -> None:
        """Write a pulse (value 1) to a command holding register."""
        async with self._lock:
            await self.async_connect()
            try:
                rq = await self._client.write_register(
                    register, 1, device_id=self._device_id
                )
            except ModbusException as err:
                raise MyAVRConnectionError(f"Modbus write failed: {err}") from err
            if rq.isError():
                raise MyAVRConnectionError(
                    f"Modbus exception writing {register}: {rq}"
                )
        _LOGGER.debug("MyAVR command written to register %s", register)
