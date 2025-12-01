from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.helpers import entity_registry as er

from custom_components.kiosker.const import DOMAIN


@pytest.mark.parametrize(
    ("unique_key", "expected_calls"),
    [
        ("ping", ["async_ping", "async_navigate_refresh"]),
        ("refresh", ["async_navigate_refresh"]),
        ("home", ["async_navigate_home"]),
        ("forward", ["async_navigate_forward"]),
        ("backward", ["async_navigate_backward"]),
        ("print", ["async_print"]),
        ("clear_cache", ["async_clear_cache"]),
        ("clear_cookies", ["async_clear_cookies"]),
        ("screensaver_interact", ["async_screensaver_interact"]),
    ],
)
async def test_buttons_call_api_and_refresh(
    hass,
    setup_integration,
    kiosker_data,
    unique_key: str,
    expected_calls: list[str],
) -> None:
    """Button presses invoke the correct client actions and refresh."""
    entry, client = await setup_integration()
    coordinator = entry.runtime_data
    coordinator.async_request_refresh = AsyncMock()

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "button", DOMAIN, f"{kiosker_data.status.device_id}_{unique_key}"
    )
    assert entity_id

    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": entity_id},
        blocking=True,
    )

    for call in expected_calls:
        getattr(client, call).assert_awaited()
    coordinator.async_request_refresh.assert_awaited_once()
