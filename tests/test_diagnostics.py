from __future__ import annotations

from homeassistant.components.diagnostics import REDACTED
from homeassistant.const import CONF_NAME

from custom_components.kiosker.const import CONF_ACCESS_TOKEN, CONF_BASE_URL
from custom_components.kiosker.diagnostics import async_get_config_entry_diagnostics


async def test_diagnostics_redacts_sensitive_fields(
    hass, setup_integration, kiosker_data
) -> None:
    """Diagnostics output omits secrets and includes device data."""
    entry, _ = await setup_integration()

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["entry"][CONF_ACCESS_TOKEN] == REDACTED
    assert result["entry"][CONF_BASE_URL] == entry.data[CONF_BASE_URL]
    assert result["entry"][CONF_NAME] == entry.data.get(CONF_NAME)

    status = result["status"]
    assert status["device"]["device_id"] == kiosker_data.status.device_id
    assert status["screensaver"] == {
        "visible": kiosker_data.screensaver.visible,
        "disabled": kiosker_data.screensaver.disabled,
    }
    assert status["blackout"]["visible"] == kiosker_data.blackout.visible
