"""Constants for the Kiosker integration."""

from datetime import timedelta
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "kiosker"
DEFAULT_NAME: Final = "Kiosker"
MANUFACTURER: Final = "Kiosker"

CONF_ACCESS_TOKEN: Final = "access_token"  # noqa: S105
CONF_BASE_URL: Final = "base_url"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=60)
MIN_SCAN_INTERVAL: Final = timedelta(seconds=10)
MAX_SCAN_INTERVAL: Final = timedelta(hours=1)
REQUEST_TIMEOUT: Final = 10

PLATFORMS: Final = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON]

SERVICE_NAVIGATE_URL: Final = "navigate_url"
SERVICE_SET_BLACKOUT: Final = "set_blackout"
SERVICE_SET_SCREENSAVER: Final = "set_screensaver"
SERVICE_SET_START_URL: Final = "set_start_url"
