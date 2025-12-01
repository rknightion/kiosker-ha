from __future__ import annotations

import sys
from pathlib import Path
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from custom_components.kiosker.api import (  # noqa: E402  # isort:skip
    BlackoutState,
    DeviceStatus,
    KioskerApiClient,
    ScreensaverState,
)
from custom_components.kiosker.const import (
    CONF_ACCESS_TOKEN,
    CONF_BASE_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from custom_components.kiosker.coordinator import KioskerData


@pytest.fixture
def base_url() -> str:
    return "http://tablet-office:8081/api/v1"


@pytest.fixture
def access_token() -> str:
    return "token-123"


@pytest.fixture
def device_status() -> DeviceStatus:
    now = dt_util.utcnow().replace(microsecond=0)
    return DeviceStatus(
        device_id="kiosk-123",
        app_version="1.2.3",
        app_name="Kiosker",
        os_version="iOS 17.4",
        model="iPad Pro",
        date=now,
        ambient_light=128.5,
        battery_level=88,
        battery_state="Charging",
        last_interaction=now - timedelta(minutes=1),
        last_motion=now - timedelta(minutes=2),
    )


@pytest.fixture
def screensaver_state() -> ScreensaverState:
    return ScreensaverState(visible=True, disabled=False)


@pytest.fixture
def blackout_state() -> BlackoutState:
    return BlackoutState(
        visible=False,
        text=None,
        background=None,
        foreground=None,
        icon=None,
        expire=None,
    )


@pytest.fixture
def kiosker_data(
    device_status: DeviceStatus,
    screensaver_state: ScreensaverState,
    blackout_state: BlackoutState,
) -> KioskerData:
    return KioskerData(
        status=device_status,
        screensaver=screensaver_state,
        blackout=blackout_state,
    )


@pytest.fixture
def mock_kiosker_client(kiosker_data: KioskerData) -> AsyncMock:
    client = AsyncMock(spec=KioskerApiClient)
    client.async_get_status.return_value = kiosker_data.status
    client.async_get_screensaver_state.return_value = kiosker_data.screensaver
    client.async_get_blackout_state.return_value = kiosker_data.blackout

    client.async_set_blackout.return_value = None
    client.async_set_screensaver.return_value = None
    client.async_set_start_url.return_value = None
    client.async_navigate_url.return_value = None
    client.async_ping.return_value = None
    client.async_print.return_value = None
    client.async_clear_cache.return_value = None
    client.async_clear_cookies.return_value = None
    client.async_navigate_home.return_value = None
    client.async_navigate_refresh.return_value = None
    client.async_navigate_forward.return_value = None
    client.async_navigate_backward.return_value = None
    client.async_screensaver_interact.return_value = None

    return client


@pytest.fixture
def mock_config_entry(
    hass,
    base_url: str,
    access_token: str,
) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Office Tablet",
        data={CONF_BASE_URL: base_url, CONF_ACCESS_TOKEN: access_token},
        options={CONF_SCAN_INTERVAL: int(DEFAULT_SCAN_INTERVAL.total_seconds())},
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def setup_integration(
    hass,
    mock_kiosker_client: AsyncMock,
    base_url: str,
    access_token: str,
    enable_custom_integrations,
):
    async def _setup(
        *,
        title: str = "Office Tablet",
        data: dict | None = None,
        options: dict | None = None,
        client: AsyncMock | None = None,
    ) -> tuple[MockConfigEntry, AsyncMock]:
        entry = MockConfigEntry(
            domain=DOMAIN,
            title=title,
            data=data
            or {
                CONF_BASE_URL: base_url,
                CONF_ACCESS_TOKEN: access_token,
            },
            options=options or {},
        )
        entry.add_to_hass(hass)
        client_to_use = client or mock_kiosker_client
        with patch(
            "custom_components.kiosker.__init__.KioskerApiClient",
            return_value=client_to_use,
        ):
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
        return entry, client_to_use

    return _setup
