"""Buttons for one-shot Kiosker actions."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .coordinator import KioskerDataUpdateCoordinator
from .entity import KioskerEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class KioskerButtonDescription(ButtonEntityDescription):
    """Describe a Kiosker button."""

    action: str | None = None


BUTTONS: tuple[KioskerButtonDescription, ...] = (
    KioskerButtonDescription(
        key="ping",
        name="Ping",
        icon="mdi:lan-pending",
        entity_category=EntityCategory.DIAGNOSTIC,
        action="ping",
    ),
    KioskerButtonDescription(
        key="refresh",
        name="Refresh Page",
        icon="mdi:refresh",
        action="refresh",
    ),
    KioskerButtonDescription(
        key="home",
        name="Go Home",
        icon="mdi:home-export-outline",
        action="home",
    ),
    KioskerButtonDescription(
        key="forward",
        name="Go Forward",
        icon="mdi:arrow-right",
        action="forward",
    ),
    KioskerButtonDescription(
        key="backward",
        name="Go Back",
        icon="mdi:arrow-left",
        action="backward",
    ),
    KioskerButtonDescription(
        key="print",
        name="Print Page",
        icon="mdi:printer",
        action="print",
    ),
    KioskerButtonDescription(
        key="clear_cache",
        name="Clear Cache",
        icon="mdi:cached",
        entity_category=EntityCategory.CONFIG,
        action="clear_cache",
    ),
    KioskerButtonDescription(
        key="clear_cookies",
        name="Clear Cookies",
        icon="mdi:cookie-alert-outline",
        entity_category=EntityCategory.CONFIG,
        action="clear_cookies",
    ),
    KioskerButtonDescription(
        key="screensaver_interact",
        name="Dismiss Screensaver",
        icon="mdi:sleep-off",
        action="screensaver_interact",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kiosker buttons."""
    coordinator: KioskerDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        KioskerActionButton(coordinator, description) for description in BUTTONS
    )


class KioskerActionButton(KioskerEntity, ButtonEntity):
    """Representation of a stateless action button."""

    entity_description: KioskerButtonDescription

    def __init__(
        self,
        coordinator: KioskerDataUpdateCoordinator,
        description: KioskerButtonDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.data.status.device_id}_{description.key}"
        )

    async def async_press(self) -> None:
        """Handle button press."""
        client = self.coordinator.client
        action = self.entity_description.action

        if action == "ping":
            _LOGGER.debug("Button ping pressed")
            await client.async_ping()
        elif action == "refresh":
            _LOGGER.debug("Button refresh pressed")
            await client.async_navigate_refresh()
        elif action == "home":
            _LOGGER.debug("Button home pressed")
            await client.async_navigate_home()
        elif action == "forward":
            _LOGGER.debug("Button forward pressed")
            await client.async_navigate_forward()
        elif action == "backward":
            _LOGGER.debug("Button backward pressed")
            await client.async_navigate_backward()
        elif action == "print":
            _LOGGER.debug("Button print pressed")
            await client.async_print()
        elif action == "clear_cache":
            _LOGGER.debug("Button clear_cache pressed")
            await client.async_clear_cache()
        elif action == "clear_cookies":
            _LOGGER.debug("Button clear_cookies pressed")
            await client.async_clear_cookies()
        elif action == "screensaver_interact":
            _LOGGER.debug("Button screensaver_interact pressed")
            await client.async_screensaver_interact()

        await self.coordinator.async_request_refresh()
