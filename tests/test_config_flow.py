from __future__ import annotations

from datetime import timedelta
from ipaddress import IPv4Address, IPv6Address
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

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


def _make_zeroconf_info(
    *,
    hostname: str = "tablet-office.local.",
    name: str = "8681F678._kiosker._tcp.local.",
    uuid: str = "8681F678-F197-404E-B22D-DBA9AB60B326",
    ip_address: IPv4Address | IPv6Address | None = None,
    ip_addresses: list[IPv4Address | IPv6Address] | None = None,
    port: int | None = 8081,
) -> ZeroconfServiceInfo:
    if ip_address is None:
        ip_address = IPv4Address("10.0.50.7")
    if ip_addresses is None:
        ip_addresses = [ip_address]
    return ZeroconfServiceInfo(
        ip_address=ip_address,
        ip_addresses=ip_addresses,
        port=port,
        hostname=hostname,
        type="_kiosker._tcp.local.",
        name=name,
        properties={
            "app": "Kiosker Pro",
            "uuid": uuid,
            "version": "25.10.1 (267)",
        },
    )


async def test_user_flow_creates_entry(hass, enable_custom_integrations) -> None:
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
    ), patch("custom_components.kiosker.KioskerApiClient"):
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


async def test_zeroconf_flow_creates_entry(
    hass, enable_custom_integrations
) -> None:
    """Zeroconf flow creates an entry and prefers IPv4 addresses."""
    uuid = "8681F678-F197-404E-B22D-DBA9AB60B326"
    discovery_info = _make_zeroconf_info(
        ip_address=IPv6Address("fd6b:d9cd:7613:4c33:cba:2cf2:c6b9:b300"),
        ip_addresses=[
            IPv6Address("fd6b:d9cd:7613:4c33:cba:2cf2:c6b9:b300"),
            IPv4Address("10.0.50.7"),
        ],
        uuid=uuid,
    )
    status = DeviceStatus(
        device_id=uuid,
        app_version="25.10.1",
        app_name="Kiosker Pro",
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
    ), patch("custom_components.kiosker.KioskerApiClient"):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_ZEROCONF},
            data=discovery_info,
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "zeroconf_confirm"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_ACCESS_TOKEN: "abc123"},
        )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "tablet-office"
    assert result2["data"] == {
        CONF_BASE_URL: "http://10.0.50.7:8081/api/v1",
        CONF_ACCESS_TOKEN: "abc123",
    }


async def test_zeroconf_flow_updates_existing_entry(
    hass, enable_custom_integrations
) -> None:
    """Zeroconf rediscovery updates the stored base URL."""
    uuid = "35147876-907B-4BBF-AA0A-7D9A0741C9B7"
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Tablet Lounge",
        data={
            CONF_BASE_URL: "http://10.0.50.150:8081/api/v1",
            CONF_ACCESS_TOKEN: "token",
        },
        unique_id=uuid,
    )
    entry.add_to_hass(hass)

    discovery_info = _make_zeroconf_info(
        hostname="tablet-lounge.local.",
        name="35147876._kiosker._tcp.local.",
        uuid=uuid,
        ip_address=IPv4Address("10.0.50.154"),
        ip_addresses=[IPv4Address("10.0.50.154")],
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery_info,
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_BASE_URL] == "http://10.0.50.154:8081/api/v1"


@pytest.mark.parametrize(
    ("exception", "error"),
    [
        (KioskerInvalidAuth(), "invalid_auth"),
        (KioskerConnectionError("boom"), "cannot_connect"),
        (KioskerUnexpectedResponse("odd"), "unknown"),
    ],
)
async def test_zeroconf_flow_errors(
    hass, enable_custom_integrations, exception: Exception, error: str
) -> None:
    """Zeroconf flow maps API errors to form errors."""
    discovery_info = _make_zeroconf_info()

    with patch(
        "custom_components.kiosker.config_flow._validate_input",
        side_effect=exception,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_ZEROCONF},
            data=discovery_info,
        )
        assert result["type"] == FlowResultType.FORM

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_ACCESS_TOKEN: "abc123"},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"]["base"] == error


@pytest.mark.parametrize(
    ("exception", "error"),
    [
        (KioskerInvalidAuth(), "invalid_auth"),
        (KioskerConnectionError("boom"), "cannot_connect"),
        (KioskerUnexpectedResponse("odd"), "unknown"),
    ],
)
async def test_user_flow_errors(
    hass, enable_custom_integrations, exception: Exception, error: str
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


async def test_reauth_flow_updates_entry(
    hass, enable_custom_integrations, mock_config_entry
) -> None:
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
        patch("custom_components.kiosker.KioskerApiClient"),
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


async def test_options_flow_accepts_scan_interval(
    hass, enable_custom_integrations
) -> None:
    """Options flow stores a valid scan interval and clamps defaults."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Office Tablet",
        data={CONF_BASE_URL: "http://example.com/api/v1", CONF_ACCESS_TOKEN: "token"},
        options={CONF_SCAN_INTERVAL: 999999},
    )
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_SCAN_INTERVAL: int(DEFAULT_SCAN_INTERVAL.total_seconds())},
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_SCAN_INTERVAL] == int(
        DEFAULT_SCAN_INTERVAL.total_seconds()
    )
