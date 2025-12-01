"""Config flow for the Kiosker integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .api import KioskerApiClient
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_BASE_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)
from .exceptions import (
    KioskerConnectionError,
    KioskerInvalidAuth,
    KioskerUnexpectedResponse,
)

_LOGGER = logging.getLogger(__name__)


async def _validate_input(hass: HomeAssistant, data: dict[str, str]):
    """Validate the user input allows us to connect."""
    client = KioskerApiClient(
        hass,
        data[CONF_BASE_URL].rstrip("/"),
        data[CONF_ACCESS_TOKEN],
    )
    return await client.async_get_status()


class KioskerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kiosker."""

    VERSION = 1
    _reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_BASE_URL] = user_input[CONF_BASE_URL].rstrip("/")
            try:
                status = await _validate_input(self.hass, user_input)
            except KioskerInvalidAuth:
                _LOGGER.error("Kiosker config flow: invalid auth for %s", user_input[CONF_BASE_URL])
                errors["base"] = "invalid_auth"
            except KioskerConnectionError as err:
                _LOGGER.error("Kiosker config flow: cannot connect to %s (%s)", user_input[CONF_BASE_URL], err)
                errors["base"] = "cannot_connect"
            except KioskerUnexpectedResponse as err:
                _LOGGER.error("Kiosker config flow: unexpected response for %s (%s)", user_input[CONF_BASE_URL], err)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(status.device_id)
                self._abort_if_unique_id_configured()

                title = (
                    user_input.get(CONF_NAME)
                    or status.app_name
                    or f"{DEFAULT_NAME} {status.device_id}"
                )

                data = {
                    CONF_BASE_URL: user_input[CONF_BASE_URL],
                    CONF_ACCESS_TOKEN: user_input[CONF_ACCESS_TOKEN],
                }
                if user_input.get(CONF_NAME):
                    data[CONF_NAME] = user_input[CONF_NAME]

                return self.async_create_entry(title=title, data=data)

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_NAME): str,
                vol.Required(CONF_BASE_URL, default="http://tablet-office:8081/api/v1"): str,
                vol.Required(CONF_ACCESS_TOKEN): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_reauth(
        self, _entry_data: dict[str, str]
    ) -> FlowResult:  # pragma: no cover - exercised in HA runtime
        """Handle reauthentication."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Confirm reauthentication."""
        assert self._reauth_entry
        errors: dict[str, str] = {}

        if user_input is not None:
            update = {
                **self._reauth_entry.data,
                CONF_ACCESS_TOKEN: user_input[CONF_ACCESS_TOKEN],
            }
            try:
                await _validate_input(self.hass, update)
            except KioskerInvalidAuth:
                _LOGGER.error("Kiosker reauth: invalid auth for %s", update[CONF_BASE_URL])
                errors["base"] = "invalid_auth"
            except KioskerConnectionError as err:
                _LOGGER.error("Kiosker reauth: cannot connect to %s (%s)", update[CONF_BASE_URL], err)
                errors["base"] = "cannot_connect"
            except KioskerUnexpectedResponse as err:
                _LOGGER.error("Kiosker reauth: unexpected response for %s (%s)", update[CONF_BASE_URL], err)
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry, data=update
                )
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_ACCESS_TOKEN): str}),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow."""
        return KioskerOptionsFlow(config_entry)


class KioskerOptionsFlow(config_entries.OptionsFlow):
    """Handle Kiosker options."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.entry = entry

    async def async_step_init(
        self, user_input: dict[str, int] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.entry.options.get(
            CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds())
        )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_interval,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=int(MIN_SCAN_INTERVAL.total_seconds())),
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors={},
        )
