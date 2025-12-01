"""Data update coordinator for Kiosker."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import BlackoutState, DeviceStatus, KioskerApiClient, ScreensaverState
from .const import DOMAIN, MIN_SCAN_INTERVAL
from .exceptions import KioskerConnectionError, KioskerInvalidAuth

_LOGGER = logging.getLogger(__name__)


@dataclass
class KioskerData:
    """Container for all data pulled from the kiosk."""

    status: DeviceStatus
    screensaver: ScreensaverState | None
    blackout: BlackoutState | None


class KioskerDataUpdateCoordinator(DataUpdateCoordinator[KioskerData]):
    """Coordinator to manage data retrieval from the kiosk."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: KioskerApiClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_{entry.title}",
            update_interval=max(update_interval, MIN_SCAN_INTERVAL),
        )
        self.entry = entry
        self.client = client

    async def _async_update_data(self) -> KioskerData:
        """Fetch data from the API."""
        try:
            status, screensaver, blackout = await asyncio.gather(
                self.client.async_get_status(),
                self.client.async_get_screensaver_state(),
                self.client.async_get_blackout_state(),
            )
        except KioskerInvalidAuth as err:
            _LOGGER.debug("Kiosker auth failed during refresh: %s", err)
            raise ConfigEntryAuthFailed("Authentication failed") from err
        except KioskerConnectionError as err:
            _LOGGER.debug("Kiosker connection error during refresh: %s", err)
            raise UpdateFailed(f"Connection error: {err}") from err
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Kiosker unexpected error during refresh: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}") from err

        return KioskerData(
            status=status,
            screensaver=screensaver,
            blackout=blackout,
        )
