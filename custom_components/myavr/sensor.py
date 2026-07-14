"""Sensor platform for the MyAVR ATS Controller."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MyAVRConfigEntry
from .const import (
    CONTACTOR_MAP,
    REG_ENGINE_HOURS_CURRENT,
    REG_ENGINE_HOURS_SETPOINT,
    REG_ENGINE_HOURS_TOTAL,
    REG_GEN_FREQ,
    REG_GEN_L1,
    REG_GEN_L2,
    REG_GEN_L3,
    REG_INV_BATTERY,
    REG_MAINS_FREQ,
    REG_MAINS_L1,
    REG_MAINS_L2,
    REG_MAINS_L3,
    REG_STARTS_SINCE_OIL,
    REG_STARTS_TOTAL,
    REG_CONTACTOR_POSITION,
    START_MODE_MAP,
    REG_START_MODE,
)
from .coordinator import MyAVRCoordinator
from .entity import MyAVREntity


@dataclass(frozen=True, kw_only=True)
class MyAVRSensorDescription(SensorEntityDescription):
    """Describes a MyAVR sensor."""

    register: int
    value_fn: Callable[[int], float | int | str | None] = lambda v: v


def _tenth(value: int) -> float:
    return round(value / 10, 1)


SENSORS: tuple[MyAVRSensorDescription, ...] = (
    MyAVRSensorDescription(
        key="mains_l1",
        translation_key="mains_l1",
        register=REG_MAINS_L1,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MyAVRSensorDescription(
        key="mains_l2",
        translation_key="mains_l2",
        register=REG_MAINS_L2,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MyAVRSensorDescription(
        key="mains_l3",
        translation_key="mains_l3",
        register=REG_MAINS_L3,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MyAVRSensorDescription(
        key="gen_l1",
        translation_key="gen_l1",
        register=REG_GEN_L1,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MyAVRSensorDescription(
        key="gen_l2",
        translation_key="gen_l2",
        register=REG_GEN_L2,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MyAVRSensorDescription(
        key="gen_l3",
        translation_key="gen_l3",
        register=REG_GEN_L3,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MyAVRSensorDescription(
        key="inverter_battery",
        translation_key="inverter_battery",
        register=REG_INV_BATTERY,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_tenth,
    ),
    MyAVRSensorDescription(
        key="mains_freq",
        translation_key="mains_freq",
        register=REG_MAINS_FREQ,
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_tenth,
    ),
    MyAVRSensorDescription(
        key="gen_freq",
        translation_key="gen_freq",
        register=REG_GEN_FREQ,
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_tenth,
    ),
    MyAVRSensorDescription(
        key="engine_hours_current",
        translation_key="engine_hours_current",
        register=REG_ENGINE_HOURS_CURRENT,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MyAVRSensorDescription(
        key="engine_hours_setpoint",
        translation_key="engine_hours_setpoint",
        register=REG_ENGINE_HOURS_SETPOINT,
        native_unit_of_measurement=UnitOfTime.MINUTES,
    ),
    MyAVRSensorDescription(
        key="engine_hours_total",
        translation_key="engine_hours_total",
        register=REG_ENGINE_HOURS_TOTAL,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    MyAVRSensorDescription(
        key="starts_since_oil",
        translation_key="starts_since_oil",
        register=REG_STARTS_SINCE_OIL,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    MyAVRSensorDescription(
        key="starts_total",
        translation_key="starts_total",
        register=REG_STARTS_TOTAL,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    MyAVRSensorDescription(
        key="contactor_position",
        translation_key="contactor_position",
        register=REG_CONTACTOR_POSITION,
        device_class=SensorDeviceClass.ENUM,
        options=list(CONTACTOR_MAP.values()),
        value_fn=lambda v: CONTACTOR_MAP.get(v),
    ),
    MyAVRSensorDescription(
        key="start_mode",
        translation_key="start_mode",
        register=REG_START_MODE,
        device_class=SensorDeviceClass.ENUM,
        options=list(START_MODE_MAP.values()),
        value_fn=lambda v: START_MODE_MAP.get(v),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyAVRConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyAVR sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        MyAVRSensor(coordinator, entry.entry_id, description)
        for description in SENSORS
    )


class MyAVRSensor(MyAVREntity, SensorEntity):
    """A MyAVR register sensor."""

    entity_description: MyAVRSensorDescription

    def __init__(
        self,
        coordinator: MyAVRCoordinator,
        entry_id: str,
        description: MyAVRSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self.entity_id = ENTITY_ID_FORMAT.format(f"myavr_{description.key}")

    @property
    def native_value(self) -> float | int | str | None:
        """Return the current value."""
        raw = self.coordinator.data.get(self.entity_description.register)
        if raw is None:
            return None
        return self.entity_description.value_fn(raw)
