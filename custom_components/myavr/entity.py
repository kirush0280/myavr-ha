"""Base entity for MyAVR entities."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import MyAVRCoordinator


class MyAVREntity(CoordinatorEntity[MyAVRCoordinator]):
    """Common base for all MyAVR entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MyAVRCoordinator, entry_id: str) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name="MyAVR ATS",
        )
