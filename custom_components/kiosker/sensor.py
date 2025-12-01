"""Sensors for Kiosker status and metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

try:
    from homeassistant.const import UnitOfIlluminance

    ILLUMINANCE_UNIT = UnitOfIlluminance.LUX
except ImportError:
    try:
        from homeassistant.const import LIGHT_LUX
    except ImportError:  # pragma: no cover - fallback for very new/old HA builds
        LIGHT_LUX = "lx"
    ILLUMINANCE_UNIT = LIGHT_LUX

from .coordinator import KioskerData, KioskerDataUpdateCoordinator
from .entity import KioskerEntity


@dataclass(frozen=True)
class KioskerSensorDescription(SensorEntityDescription):
    """Describe a Kiosker sensor entity."""

    value_fn: Callable[[KioskerData], Any] = lambda _: None


SENSORS: tuple[KioskerSensorDescription, ...] = (
    KioskerSensorDescription(
        key="ambient_light",
        name="Ambient Light",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=ILLUMINANCE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.ambient_light,
    ),
    KioskerSensorDescription(
        key="battery_level",
        name="Battery Level",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.battery_level,
    ),
    KioskerSensorDescription(
        key="battery_state",
        name="Battery State",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda data: data.status.battery_state,
    ),
    KioskerSensorDescription(
        key="last_interaction",
        name="Last Interaction",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.status.last_interaction,
    ),
    KioskerSensorDescription(
        key="last_motion",
        name="Last Motion",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.status.last_motion,
    ),
    KioskerSensorDescription(
        key="app_version",
        name="App Version",
        icon="mdi:application",
        value_fn=lambda data: data.status.app_version,
    ),
    KioskerSensorDescription(
        key="os_version",
        name="OS Version",
        icon="mdi:apple-ios",
        value_fn=lambda data: data.status.os_version,
    ),
    KioskerSensorDescription(
        key="model",
        name="Device Model",
        icon="mdi:tablet-ipad",
        value_fn=lambda data: data.status.model,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kiosker sensors."""
    coordinator: KioskerDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        KioskerSensor(coordinator, description) for description in SENSORS
    )


class KioskerSensor(KioskerEntity, SensorEntity):
    """Representation of a Kiosker sensor."""

    entity_description: KioskerSensorDescription

    def __init__(
        self,
        coordinator: KioskerDataUpdateCoordinator,
        description: KioskerSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.data.status.device_id}_{description.key}"
        )

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def icon(self) -> str | None:
        """Return a dynamic icon when appropriate."""
        if self.entity_description.key == "battery_state":
            level = self.coordinator.data.status.battery_level
            charging = (
                str(self.coordinator.data.status.battery_state).lower()
                == "charging"
            )
            return icon_for_battery_level(level, charging=charging)
        return super().icon
