"""Button platform for the MyAVR ATS Controller."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.components.button import ENTITY_ID_FORMAT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MyAVRConfigEntry
from .const import (
    REG_CMD_START,
    REG_CMD_STOP,
    REG_CMD_SCHEDULE_ON,
    REG_CMD_SCHEDULE_OFF,
)
from .coordinator import MyAVRCoordinator
from .entity import MyAVREntity


@dataclass(frozen=True, kw_only=True)
class MyAVRButtonDescription(ButtonEntityDescription):
    """Describes a MyAVR button."""

    register: int


BUTTONS: tuple[MyAVRButtonDescription, ...] = (
    MyAVRButtonDescription(
        key="start_generator",
        translation_key="start_generator",
        register=REG_CMD_START,
    ),
    MyAVRButtonDescription(
        key="stop_generator",
        translation_key="stop_generator",
        register=REG_CMD_STOP,
    ),
    MyAVRButtonDescription(
        key="schedule_on",
        translation_key="schedule_on",
        register=REG_CMD_SCHEDULE_ON,
    ),
    MyAVRButtonDescription(
        key="schedule_off",
        translation_key="schedule_off",
        register=REG_CMD_SCHEDULE_OFF,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyAVRConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyAVR buttons."""
    coordinator = entry.runtime_data
    async_add_entities(
        MyAVRButton(coordinator, entry.entry_id, description)
        for description in BUTTONS
    )


class MyAVRButton(MyAVREntity, ButtonEntity):
    """A MyAVR command button."""

    entity_description: MyAVRButtonDescription

    def __init__(
        self,
        coordinator: MyAVRCoordinator,
        entry_id: str,
        description: MyAVRButtonDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self.entity_id = ENTITY_ID_FORMAT.format(f"myavr_{description.key}")

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_send_command(self.entity_description.register)
