"""Base entities for the Kiosker integration."""

from __future__ import annotations

from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import KioskerDataUpdateCoordinator


class KioskerEntity(CoordinatorEntity[KioskerDataUpdateCoordinator]):
    """Common entity behavior for Kiosker entities."""

    _attr_has_entity_name = True
    coordinator: KioskerDataUpdateCoordinator

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
            model=f"{status.model} ({status.app_name})"
            if status.app_name
            else status.model,
            sw_version=(
                f"{status.app_name} {status.app_version}"
                if status.app_name
                else status.app_version
            ),
            serial_number=status.device_id,
        )
