from __future__ import annotations

from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.icon import icon_for_battery_level
from homeassistant.util import dt as dt_util

from custom_components.kiosker.const import DOMAIN, MANUFACTURER


async def test_entities_and_device_info(hass, setup_integration, kiosker_data) -> None:
    """Entities are created with correct state and device metadata."""
    entry, _client = await setup_integration()
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    device_id = kiosker_data.status.device_id

    battery_entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, f"{device_id}_battery_level"
    )
    ambient_entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, f"{device_id}_ambient_light"
    )
    battery_state_entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, f"{device_id}_battery_state"
    )
    interaction_entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, f"{device_id}_last_interaction"
    )
    assert battery_state_entity_id
    blackout_entity_id = entity_registry.async_get_entity_id(
        "binary_sensor", DOMAIN, f"{device_id}_blackout_active"
    )
    screensaver_entity_id = entity_registry.async_get_entity_id(
        "binary_sensor", DOMAIN, f"{device_id}_screensaver_visible"
    )

    assert battery_entity_id and ambient_entity_id and interaction_entity_id
    assert blackout_entity_id and screensaver_entity_id

    battery_state = hass.states.get(battery_entity_id)
    ambient_state = hass.states.get(ambient_entity_id)
    interaction_state = hass.states.get(interaction_entity_id)
    blackout_state = hass.states.get(blackout_entity_id)
    screensaver_state = hass.states.get(screensaver_entity_id)
    battery_state_sensor = hass.states.get(battery_state_entity_id)

    assert battery_state.state == str(kiosker_data.status.battery_level)
    assert ambient_state.state == str(kiosker_data.status.ambient_light)
    assert (
        interaction_state.state
        == dt_util.as_utc(kiosker_data.status.last_interaction).isoformat()
    )
    assert blackout_state.state == "off"
    assert screensaver_state.state == "on"

    expected_icon = icon_for_battery_level(
        kiosker_data.status.battery_level, charging=True
    )
    assert battery_state_sensor.attributes["icon"] == expected_icon

    entity_entry = entity_registry.async_get(battery_entity_id)
    assert entity_entry is not None
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(entity_entry.device_id)
    assert device is not None
    assert device.manufacturer == MANUFACTURER
    assert device.name == entry.title
    assert kiosker_data.status.model in device.model


async def test_entry_runtime_data_populated(
    hass, setup_integration, kiosker_data
) -> None:
    """Coordinator is stored on the config entry."""
    entry, _ = await setup_integration()
    coordinator = entry.runtime_data
    assert coordinator is not None
    assert coordinator.data.status.device_id == kiosker_data.status.device_id
