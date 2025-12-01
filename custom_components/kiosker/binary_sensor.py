"""Binary sensors for Kiosker."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import KioskerData, KioskerDataUpdateCoordinator
from .entity import KioskerEntity


@dataclass(frozen=True)
class KioskerBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a Kiosker binary sensor."""

    value_fn: Callable[[KioskerData], bool | None] = lambda _: None


BINARY_SENSORS: tuple[KioskerBinarySensorDescription, ...] = (
    KioskerBinarySensorDescription(
        key="screensaver_visible",
        name="Screensaver Active",
        icon="mdi:sleep",
        value_fn=lambda data: data.screensaver.visible
        if data.screensaver
        else None,
    ),
    KioskerBinarySensorDescription(
        key="screensaver_disabled",
        name="Screensaver Disabled",
        icon="mdi:sleep-off",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.screensaver.disabled
        if data.screensaver
        else None,
    ),
    KioskerBinarySensorDescription(
        key="blackout_active",
        name="Blackout Active",
        icon="mdi:cancel",
        value_fn=lambda data: data.blackout.visible if data.blackout else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kiosker binary sensors."""
    coordinator: KioskerDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        KioskerBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    )


class KioskerBinarySensor(KioskerEntity, BinarySensorEntity):
    """Representation of a Kiosker binary sensor."""

    entity_description: KioskerBinarySensorDescription

    def __init__(
        self,
        coordinator: KioskerDataUpdateCoordinator,
        description: KioskerBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.data.status.device_id}_{description.key}"
        )

    @property
    def is_on(self) -> bool | None:
        """Return the state of the binary sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
