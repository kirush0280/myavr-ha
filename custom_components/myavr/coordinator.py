"""DataUpdateCoordinator for the MyAVR ATS controller."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .client import MyAVRClient, MyAVRError
from .const import CONTACTOR_GENERATOR, DOMAIN, REG_CONTACTOR_POSITION

_LOGGER = logging.getLogger(__name__)


class MyAVRCoordinator(DataUpdateCoordinator[dict[int, int]]):
    """Polls the MyAVR controller and shares register data with entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MyAVRClient,
        scan_interval: int,
        entry_id: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self.run_started_at: datetime | None = None
        self.last_run_duration: int | None = None
        self._last_contactor_position: int | None = None
        self._first_snapshot = True
        self._store: Store[dict[str, Any]] = Store(
            hass, 1, f"{DOMAIN}.{entry_id}.run_state"
        )

    async def async_load_run_state(self) -> None:
        """Restore generator run tracking across Home Assistant restarts."""
        if not (stored := await self._store.async_load()):
            return

        self.last_run_duration = stored.get("last_run_duration")
        self._last_contactor_position = stored.get("contactor_position")
        started_at = stored.get("run_started_at")
        if isinstance(started_at, str):
            self.run_started_at = dt_util.parse_datetime(started_at)

    def _run_state(self) -> dict[str, Any]:
        """Return serializable run tracking state."""
        return {
            "contactor_position": self._last_contactor_position,
            "run_started_at": (
                self.run_started_at.isoformat() if self.run_started_at else None
            ),
            "last_run_duration": self.last_run_duration,
        }

    async def _async_track_run(self, data: dict[int, int]) -> None:
        """Track generator contactor transitions and persist run duration."""
        position = data.get(REG_CONTACTOR_POSITION)
        if position not in (1, 2, CONTACTOR_GENERATOR):
            return

        previous = self._last_contactor_position
        self._last_contactor_position = position
        if self._first_snapshot:
            self._first_snapshot = False
            # A run ending while HA was down has no observable end timestamp.
            if position != CONTACTOR_GENERATOR and previous == CONTACTOR_GENERATOR:
                self.run_started_at = None
                self.last_run_duration = None
            elif position == CONTACTOR_GENERATOR and previous != CONTACTOR_GENERATOR:
                self.run_started_at = None
                self.last_run_duration = None
        elif position == previous:
            return
        elif position == CONTACTOR_GENERATOR:
            self.run_started_at = dt_util.utcnow()
        elif previous == CONTACTOR_GENERATOR:
            self.last_run_duration = (
                max(0, round((dt_util.utcnow() - self.run_started_at).total_seconds() / 60))
                if self.run_started_at is not None
                else None
            )
            self.run_started_at = None

        await self._store.async_save(self._run_state())

    async def _async_update_data(self) -> dict[int, int]:
        """Fetch the latest register snapshot."""
        try:
            data = await self.client.async_read_all()
        except MyAVRError as err:
            raise UpdateFailed(str(err)) from err

        await self._async_track_run(data)
        return data

    async def async_send_command(self, register: int) -> None:
        """Send a command pulse and refresh state shortly after."""
        await self.client.async_write_command(register)
        await self.async_request_refresh()
