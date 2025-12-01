from __future__ import annotations

from datetime import timedelta

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.kiosker.coordinator import (
    KioskerData,
    KioskerDataUpdateCoordinator,
)
from custom_components.kiosker.const import MIN_SCAN_INTERVAL
from custom_components.kiosker.exceptions import (
    KioskerConnectionError,
    KioskerInvalidAuth,
)


async def test_coordinator_fetches_data(
    hass, mock_config_entry, mock_kiosker_client, kiosker_data: KioskerData
) -> None:
    """Coordinator returns aggregated kiosk data."""
    coordinator = KioskerDataUpdateCoordinator(
        hass,
        mock_config_entry,
        mock_kiosker_client,
        timedelta(seconds=30),
    )

    result = await coordinator._async_update_data()

    assert result == kiosker_data
    assert coordinator.update_interval == timedelta(seconds=30)


async def test_coordinator_enforces_min_interval(
    hass, mock_config_entry, mock_kiosker_client
) -> None:
    """Coordinator clamps update interval to the minimum."""
    coordinator = KioskerDataUpdateCoordinator(
        hass,
        mock_config_entry,
        mock_kiosker_client,
        timedelta(seconds=1),
    )

    assert coordinator.update_interval == MIN_SCAN_INTERVAL


async def test_coordinator_handles_invalid_auth(
    hass, mock_config_entry, mock_kiosker_client
) -> None:
    """Invalid auth during refresh raises ConfigEntryAuthFailed."""
    mock_kiosker_client.async_get_status.side_effect = KioskerInvalidAuth("bad token")
    coordinator = KioskerDataUpdateCoordinator(
        hass,
        mock_config_entry,
        mock_kiosker_client,
        timedelta(seconds=15),
    )

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


async def test_coordinator_handles_connection_error(
    hass, mock_config_entry, mock_kiosker_client
) -> None:
    """Connection errors become UpdateFailed."""
    mock_kiosker_client.async_get_status.side_effect = KioskerConnectionError("down")
    coordinator = KioskerDataUpdateCoordinator(
        hass,
        mock_config_entry,
        mock_kiosker_client,
        timedelta(seconds=15),
    )

    with pytest.raises(UpdateFailed) as err:
        await coordinator._async_update_data()

    assert "Connection error" in str(err.value)


async def test_coordinator_handles_unexpected_error(
    hass, mock_config_entry, mock_kiosker_client
) -> None:
    """Unexpected errors surface as UpdateFailed."""
    mock_kiosker_client.async_get_status.side_effect = RuntimeError("boom")
    coordinator = KioskerDataUpdateCoordinator(
        hass,
        mock_config_entry,
        mock_kiosker_client,
        timedelta(seconds=15),
    )

    with pytest.raises(UpdateFailed) as err:
        await coordinator._async_update_data()

    assert "Unexpected error: boom" in str(err.value)
