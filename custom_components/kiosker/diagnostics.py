"""Diagnostics support for Kiosker."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_BASE_URL, CONF_NAME
from homeassistant.core import HomeAssistant

from .coordinator import KioskerDataUpdateCoordinator

TO_REDACT = {CONF_ACCESS_TOKEN}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: KioskerDataUpdateCoordinator = entry.runtime_data
    data = coordinator.data

    diagnostics: dict[str, Any] = {
        "entry": async_redact_data(
            {
                "title": entry.title,
                CONF_BASE_URL: entry.data.get(CONF_BASE_URL),
                CONF_NAME: entry.data.get(CONF_NAME),
                CONF_ACCESS_TOKEN: entry.data.get(CONF_ACCESS_TOKEN),
            },
            TO_REDACT,
        ),
        "status": None,
    }

    if data:
        diagnostics["status"] = {
            "device": {
                "device_id": data.status.device_id,
                "app_name": data.status.app_name,
                "app_version": data.status.app_version,
                "os_version": data.status.os_version,
                "model": data.status.model,
            },
            "metrics": {
                "ambient_light": data.status.ambient_light,
                "battery_level": data.status.battery_level,
                "battery_state": data.status.battery_state,
                "last_interaction": data.status.last_interaction,
                "last_motion": data.status.last_motion,
            },
            "screensaver": asdict(data.screensaver) if data.screensaver else None,
            "blackout": asdict(data.blackout) if data.blackout else None,
        }

    return diagnostics
