"""Select platform for the MyAVR ATS Controller (start mode)."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.components.select import ENTITY_ID_FORMAT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MyAVRConfigEntry
from .const import (
    REG_CMD_MODE_AUTO,
    REG_CMD_MODE_ECO,
    REG_CMD_MODE_MANUAL,
    REG_START_MODE,
    START_MODE_MAP,
)
from .coordinator import MyAVRCoordinator
from .entity import MyAVREntity

# Option label -> command register that activates that mode.
MODE_TO_COMMAND: dict[str, int] = {
    "manual": REG_CMD_MODE_MANUAL,
    "auto": REG_CMD_MODE_AUTO,
    "eco": REG_CMD_MODE_ECO,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyAVRConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MyAVR start mode select."""
    coordinator = entry.runtime_data
    async_add_entities([MyAVRModeSelect(coordinator, entry.entry_id)])


class MyAVRModeSelect(MyAVREntity, SelectEntity):
    """Start mode select: manual / auto / eco."""

    _attr_translation_key = "start_mode"
    _attr_options = list(START_MODE_MAP.values())

    def __init__(
        self, coordinator: MyAVRCoordinator, entry_id: str
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_start_mode_select"
        self.entity_id = ENTITY_ID_FORMAT.format("myavr_start_mode")

    @property
    def current_option(self) -> str | None:
        """Return the currently selected mode."""
        raw = self.coordinator.data.get(REG_START_MODE)
        if raw is None:
            return None
        return START_MODE_MAP.get(raw)

    async def async_select_option(self, option: str) -> None:
        """Change the start mode."""
        register = MODE_TO_COMMAND.get(option)
        if register is None:
            return
        await self.coordinator.async_send_command(register)
