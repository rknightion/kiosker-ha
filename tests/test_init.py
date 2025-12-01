from __future__ import annotations

from custom_components.kiosker.const import CONF_SCAN_INTERVAL, DOMAIN, MIN_SCAN_INTERVAL


async def test_async_setup_entry_stores_runtime_data(
    hass, setup_integration, mock_kiosker_client
) -> None:
    """Setup stores coordinator and client on hass data and entry."""
    entry, client = await setup_integration(options={CONF_SCAN_INTERVAL: 1})

    assert DOMAIN in hass.data
    domain_data = hass.data[DOMAIN]
    assert entry.entry_id in domain_data["entries"]

    coordinator = entry.runtime_data
    assert coordinator.client is client
    assert coordinator.update_interval == MIN_SCAN_INTERVAL
