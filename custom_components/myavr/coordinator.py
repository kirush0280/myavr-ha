"""DataUpdateCoordinator for the MyAVR ATS controller."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import MyAVRClient, MyAVRError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MyAVRCoordinator(DataUpdateCoordinator[dict[int, int]]):
    """Polls the MyAVR controller and shares register data with entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MyAVRClient,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[int, int]:
        """Fetch the latest register snapshot."""
        try:
            return await self.client.async_read_all()
        except MyAVRError as err:
            raise UpdateFailed(str(err)) from err

    async def async_send_command(self, register: int) -> None:
        """Send a command pulse and refresh state shortly after."""
        await self.client.async_write_command(register)
        await self.async_request_refresh()
