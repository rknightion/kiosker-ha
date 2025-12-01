from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.kiosker.api import (
    BlackoutState,
    DeviceStatus,
    KioskerApiClient,
    ScreensaverState,
)
from custom_components.kiosker.const import (
    CONF_ACCESS_TOKEN,
    CONF_BASE_URL,
    DOMAIN,
    SERVICE_NAVIGATE_URL,
    SERVICE_SET_BLACKOUT,
    SERVICE_SET_SCREENSAVER,
    SERVICE_SET_START_URL,
)


async def test_services_call_client_and_refresh(hass, setup_integration) -> None:
    """Domain services invoke the client and refresh when appropriate."""
    entry, client = await setup_integration()
    coordinator = entry.runtime_data
    coordinator.async_request_refresh = AsyncMock()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_NAVIGATE_URL,
        {"url": "https://example.com"},
        blocking=True,
    )
    client.async_navigate_url.assert_awaited_once_with("https://example.com")
    coordinator.async_request_refresh.assert_awaited_once()

    coordinator.async_request_refresh.reset_mock()
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_BLACKOUT,
        {"visible": True, "text": "Hello"},
        blocking=True,
    )
    client.async_set_blackout.assert_awaited_once_with(
        visible=True,
        text="Hello",
        background=None,
        foreground=None,
        icon=None,
        expire=None,
    )
    coordinator.async_request_refresh.assert_awaited_once()

    coordinator.async_request_refresh.reset_mock()
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_SCREENSAVER,
        {"disabled": True},
        blocking=True,
    )
    client.async_set_screensaver.assert_awaited_once_with(
        disabled=True, visible=None
    )
    coordinator.async_request_refresh.assert_awaited_once()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_START_URL,
        {"url": "https://start"},
        blocking=True,
    )
    client.async_set_start_url.assert_awaited_once_with("https://start")


async def test_service_device_resolution(
    hass,
    setup_integration,
) -> None:
    """Services target the correct entry when multiple devices exist."""
    entry1, client1 = await setup_integration(title="Tablet 1")

    status2 = DeviceStatus(
        device_id="kiosk-456",
        app_version="2.0.0",
        app_name="Kiosker",
        os_version="iOS 18",
        model="iPad Air",
        date=dt_util.utcnow(),
        ambient_light=50.0,
        battery_level=20,
        battery_state="Discharging",
        last_interaction=None,
        last_motion=None,
    )
    client2 = AsyncMock(spec=KioskerApiClient)
    client2.async_get_status = AsyncMock(return_value=status2)
    client2.async_get_screensaver_state = AsyncMock(
        return_value=ScreensaverState(visible=False, disabled=False)
    )
    client2.async_get_blackout_state = AsyncMock(
        return_value=BlackoutState(
            visible=False,
            text=None,
            background=None,
            foreground=None,
            icon=None,
            expire=None,
        )
    )
    client2.async_navigate_url = AsyncMock(return_value=None)

    entry2, _ = await setup_integration(
        title="Tablet 2",
        data={
            CONF_BASE_URL: "http://second/api/v1",
            CONF_ACCESS_TOKEN: "other",
        },
        client=client2,
    )

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_NAVIGATE_URL,
            {"url": "https://example.com"},
            blocking=True,
        )

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, f"{status2.device_id}_battery_level"
    )
    assert entity_id
    device_id = entity_registry.async_get(entity_id).device_id
    coordinator2 = entry2.runtime_data
    coordinator2.async_request_refresh = AsyncMock()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_NAVIGATE_URL,
        {ATTR_DEVICE_ID: device_id, "url": "https://example.com/device2"},
        blocking=True,
    )

    client2.async_navigate_url.assert_awaited_once_with("https://example.com/device2")
    assert client1.async_navigate_url.await_count == 0
    coordinator2.async_request_refresh.assert_awaited_once()


async def test_unload_removes_services(hass, setup_integration) -> None:
    """Services are removed once the final entry unloads."""
    entry, _ = await setup_integration()
    assert hass.services.has_service(DOMAIN, SERVICE_NAVIGATE_URL)

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, SERVICE_NAVIGATE_URL)
