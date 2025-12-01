from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.util import dt as dt_util

from custom_components.kiosker.api import DeviceStatus
from custom_components.kiosker.const import (
    CONF_ACCESS_TOKEN,
    CONF_BASE_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from custom_components.kiosker.exceptions import (
    KioskerConnectionError,
    KioskerInvalidAuth,
    KioskerUnexpectedResponse,
)


async def test_user_flow_creates_entry(hass) -> None:
    """Config flow creates an entry when validation succeeds."""
    user_input = {
        CONF_NAME: "Front Tablet",
        CONF_BASE_URL: "http://example.com/api/v1/",
        CONF_ACCESS_TOKEN: "abc123",
    }
    status = DeviceStatus(
        device_id="device-1",
        app_version="1.0.0",
        app_name="Kiosker",
        os_version="iOS 17",
        model="iPad",
        date=dt_util.utcnow(),
        ambient_light=None,
        battery_level=None,
        battery_state=None,
        last_interaction=None,
        last_motion=None,
    )

    with patch(
        "custom_components.kiosker.config_flow._validate_input",
        return_value=status,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data=user_input,
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Front Tablet"
    assert result["data"] == {
        CONF_BASE_URL: "http://example.com/api/v1",
        CONF_ACCESS_TOKEN: "abc123",
        CONF_NAME: "Front Tablet",
    }


@pytest.mark.parametrize(
    ("exception", "error"),
    [
        (KioskerInvalidAuth(), "invalid_auth"),
        (KioskerConnectionError("boom"), "cannot_connect"),
        (KioskerUnexpectedResponse("odd"), "unknown"),
    ],
)
async def test_user_flow_errors(
    hass, exception: Exception, error: str
) -> None:
    """Config flow maps API errors to form errors."""
    user_input = {
        CONF_BASE_URL: "http://example.com/api/v1",
        CONF_ACCESS_TOKEN: "abc123",
    }
    with patch(
        "custom_components.kiosker.config_flow._validate_input",
        side_effect=exception,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data=user_input,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == error


async def test_reauth_flow_updates_entry(hass, mock_config_entry) -> None:
    """Reauth flow stores the new token and reloads the entry."""
    status = DeviceStatus(
        device_id="kiosk-123",
        app_version="1.0.0",
        app_name="Kiosker",
        os_version="iOS 17",
        model="iPad",
        date=dt_util.utcnow(),
        ambient_light=1.0,
        battery_level=50,
        battery_state="Charging",
        last_interaction=dt_util.utcnow() - timedelta(minutes=1),
        last_motion=dt_util.utcnow() - timedelta(minutes=2),
    )

    with (
        patch(
            "custom_components.kiosker.config_flow._validate_input",
            return_value=status,
        ),
        patch.object(
            hass.config_entries, "async_reload", AsyncMock()
        ) as reload_mock,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_REAUTH,
                "entry_id": mock_config_entry.entry_id,
            },
            data=mock_config_entry.data,
        )
        assert result["type"] == FlowResultType.FORM
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_ACCESS_TOKEN: "new-token"}
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "reauth_successful"
    assert mock_config_entry.data[CONF_ACCESS_TOKEN] == "new-token"
    reload_mock.assert_awaited_once_with(mock_config_entry.entry_id)


async def test_options_flow_accepts_scan_interval(hass, mock_config_entry) -> None:
    """Options flow stores a valid scan interval and clamps defaults."""
    mock_config_entry.options = {CONF_SCAN_INTERVAL: 999999}
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] == FlowResultType.FORM

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_SCAN_INTERVAL: int(DEFAULT_SCAN_INTERVAL.total_seconds())},
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_SCAN_INTERVAL] == int(
        DEFAULT_SCAN_INTERVAL.total_seconds()
    )
