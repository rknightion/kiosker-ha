"""Base entities for the Kiosker integration."""

from __future__ import annotations

from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import KioskerData, KioskerDataUpdateCoordinator


class KioskerEntity(CoordinatorEntity[KioskerData]):
    """Common entity behavior for Kiosker entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: KioskerDataUpdateCoordinator) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device metadata."""
        if not self.coordinator.data:
            return None
        status = self.coordinator.data.status
        name = (
            self.coordinator.entry.data.get(CONF_NAME)
            or self.coordinator.entry.title
            or status.app_name
        )
        return DeviceInfo(
            identifiers={(DOMAIN, status.device_id)},
            name=name,
            manufacturer=MANUFACTURER,
            model=status.model,
            sw_version=status.app_version,
        )
