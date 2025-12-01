"""The Kiosker integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    HomeAssistantError,
)
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .api import KioskerApiClient
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_BASE_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
    SERVICE_NAVIGATE_URL,
    SERVICE_SET_BLACKOUT,
    SERVICE_SET_SCREENSAVER,
    SERVICE_SET_START_URL,
)
from .coordinator import KioskerDataUpdateCoordinator
from .exceptions import KioskerConnectionError, KioskerInvalidAuth

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Kiosker component (empty)."""
    hass.data.setdefault(DOMAIN, {"entries": {}, "services_registered": False})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Kiosker from a config entry."""
    domain_data = hass.data.setdefault(
        DOMAIN, {"entries": {}, "services_registered": False}
    )
    _LOGGER.debug("Setting up Kiosker entry %s (%s)", entry.entry_id, entry.title)
    client = KioskerApiClient(
        hass,
        entry.data[CONF_BASE_URL],
        entry.data[CONF_ACCESS_TOKEN],
    )

    interval_seconds = entry.options.get(
        CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds())
    )
    coordinator = KioskerDataUpdateCoordinator(
        hass,
        entry,
        client,
        timedelta(seconds=interval_seconds),
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except KioskerInvalidAuth as err:
        raise ConfigEntryAuthFailed from err
    except KioskerConnectionError as err:
        raise ConfigEntryNotReady from err

    domain_data["entries"][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))

    if not domain_data["services_registered"]:
        _register_services(hass)
        domain_data["services_registered"] = True

    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        domain_data = hass.data.get(DOMAIN, {})
        entries = domain_data.get("entries", {})
        entries.pop(entry.entry_id, None)
        if not entries and domain_data.get("services_registered"):
            hass.services.async_remove(DOMAIN, SERVICE_NAVIGATE_URL)
            hass.services.async_remove(DOMAIN, SERVICE_SET_BLACKOUT)
            hass.services.async_remove(DOMAIN, SERVICE_SET_SCREENSAVER)
            hass.services.async_remove(DOMAIN, SERVICE_SET_START_URL)
            domain_data["services_registered"] = False
    return unload_ok


def _get_entry_from_call(hass: HomeAssistant, call: ServiceCall) -> dict[str, Any]:
    """Resolve which config entry a service call targets."""
    domain_data = hass.data.get(DOMAIN, {})
    entries: dict[str, dict[str, Any]] = domain_data.get("entries", {})

    device_id = call.data.get(ATTR_DEVICE_ID)
    if isinstance(device_id, list):
        device_id = device_id[0] if device_id else None
    if device_id:
        device_registry = dr.async_get(hass)
        device = device_registry.async_get(device_id)
        if device:
            for entry_id in device.config_entries:
                if entry_id in entries:
                    return entries[entry_id]
        raise HomeAssistantError("Could not resolve Kiosker device for service call")

    if len(entries) == 1:
        return next(iter(entries.values()))

    raise HomeAssistantError(
        "Multiple Kiosker entries are configured; provide device_id to target one"
    )


def _register_services(hass: HomeAssistant) -> None:
    """Register Kiosker services."""
    from homeassistant.helpers import config_validation as cv  # inline import for HA typing

    navigate_url_schema = vol.Schema(
        {
            vol.Optional(ATTR_DEVICE_ID): str,
            vol.Required("url"): cv.url,
        }
    )

    set_start_url_schema = vol.Schema(
        {
            vol.Optional(ATTR_DEVICE_ID): str,
            vol.Required("url"): cv.url,
        }
    )

    set_blackout_schema = vol.Schema(
        {
            vol.Optional(ATTR_DEVICE_ID): str,
            vol.Required("visible"): bool,
            vol.Optional("text"): str,
            vol.Optional("background"): str,
            vol.Optional("foreground"): str,
            vol.Optional("icon"): str,
            vol.Optional("expire"): vol.Coerce(int),
        }
    )

    set_screensaver_schema = vol.Schema(
        {
            vol.Optional(ATTR_DEVICE_ID): str,
            vol.Required("disabled"): bool,
            vol.Optional("visible"): bool,
        }
    )

    async def handle_navigate_url(call: ServiceCall) -> None:
        entry_data = _get_entry_from_call(hass, call)
        client: KioskerApiClient = entry_data["client"]
        coordinator: KioskerDataUpdateCoordinator = entry_data["coordinator"]
        _LOGGER.debug("Service navigate_url invoked for %s", call.data.get("url"))
        await client.async_navigate_url(call.data["url"])
        await coordinator.async_request_refresh()

    async def handle_set_blackout(call: ServiceCall) -> None:
        entry_data = _get_entry_from_call(hass, call)
        client: KioskerApiClient = entry_data["client"]
        coordinator: KioskerDataUpdateCoordinator = entry_data["coordinator"]
        _LOGGER.debug("Service set_blackout invoked: %s", call.data)
        await client.async_set_blackout(
            visible=call.data["visible"],
            text=call.data.get("text"),
            background=call.data.get("background"),
            foreground=call.data.get("foreground"),
            icon=call.data.get("icon"),
            expire=call.data.get("expire"),
        )
        await coordinator.async_request_refresh()

    async def handle_set_screensaver(call: ServiceCall) -> None:
        entry_data = _get_entry_from_call(hass, call)
        client: KioskerApiClient = entry_data["client"]
        coordinator: KioskerDataUpdateCoordinator = entry_data["coordinator"]
        _LOGGER.debug("Service set_screensaver invoked: %s", call.data)
        await client.async_set_screensaver(
            disabled=call.data["disabled"],
            visible=call.data.get("visible"),
        )
        await coordinator.async_request_refresh()

    async def handle_set_start_url(call: ServiceCall) -> None:
        entry_data = _get_entry_from_call(hass, call)
        client: KioskerApiClient = entry_data["client"]
        _LOGGER.debug("Service set_start_url invoked for %s", call.data.get("url"))
        await client.async_set_start_url(call.data["url"])

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAVIGATE_URL,
        handle_navigate_url,
        schema=navigate_url_schema,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_BLACKOUT,
        handle_set_blackout,
        schema=set_blackout_schema,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SCREENSAVER,
        handle_set_screensaver,
        schema=set_screensaver_schema,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_START_URL,
        handle_set_start_url,
        schema=set_start_url_schema,
    )
