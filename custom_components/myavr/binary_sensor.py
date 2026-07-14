"""Binary sensor platform for the MyAVR ATS Controller."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.binary_sensor import ENTITY_ID_FORMAT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MyAVRConfigEntry
from .const import (
    REG_ERROR_FIRST,
    REG_NO_ERRORS,
    REG_PREVENTIVE_START_FLAG,
    REG_SCHEDULE_ENABLED,
    REG_SCHEDULE_INHIBIT,
    REG_START_COMMAND_SENT,
)
from .coordinator import MyAVRCoordinator
from .entity import MyAVREntity


@dataclass(frozen=True, kw_only=True)
class MyAVRBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a MyAVR binary sensor."""

    register: int
    value_fn: Callable[[int], bool] = lambda v: bool(v)


def _inverted(value: int) -> bool:
    """Inverted logic (0 = on)."""
    return not bool(value)


BINARY_SENSORS: tuple[MyAVRBinarySensorDescription, ...] = (
    MyAVRBinarySensorDescription(
        key="no_errors",
        translation_key="no_errors",
        register=REG_NO_ERRORS,
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=_inverted,  # 1 = no errors -> problem=off
    ),
    MyAVRBinarySensorDescription(
        key="start_command_sent",
        translation_key="start_command_sent",
        register=REG_START_COMMAND_SENT,
    ),
    MyAVRBinarySensorDescription(
        key="preventive_start_flag",
        translation_key="preventive_start_flag",
        register=REG_PREVENTIVE_START_FLAG,
    ),
    MyAVRBinarySensorDescription(
        key="schedule_enabled",
        translation_key="schedule_enabled",
        register=REG_SCHEDULE_ENABLED,
    ),
    MyAVRBinarySensorDescription(
        key="schedule_inhibit",
        translation_key="schedule_inhibit",
        register=REG_SCHEDULE_INHIBIT,
    ),
)


def _make_error_sensors() -> list[MyAVRBinarySensorDescription]:
    """Generate individual binary sensors for errors 1..20."""
    result = []
    for error_num in range(1, 21):
        reg = REG_ERROR_FIRST + (error_num - 1)
        result.append(
            MyAVRBinarySensorDescription(
                key=f"error_{error_num}",
                translation_key=f"error_{error_num}",
                register=reg,
                device_class=BinarySensorDeviceClass.PROBLEM,
            )
        )
    return result


ALL_BINARY_SENSORS = BINARY_SENSORS + tuple(_make_error_sensors())


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyAVRConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyAVR binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        MyAVRBinarySensor(coordinator, entry.entry_id, description)
        for description in ALL_BINARY_SENSORS
    )


class MyAVRBinarySensor(MyAVREntity, BinarySensorEntity):
    """A MyAVR binary sensor."""

    entity_description: MyAVRBinarySensorDescription

    def __init__(
        self,
        coordinator: MyAVRCoordinator,
        entry_id: str,
        description: MyAVRBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self.entity_id = ENTITY_ID_FORMAT.format(f"myavr_{description.key}")

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        raw = self.coordinator.data.get(self.entity_description.register)
        if raw is None:
            return None
        return self.entity_description.value_fn(raw)
