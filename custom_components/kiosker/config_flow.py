"""Config flow for the Kiosker integration."""

from __future__ import annotations

import logging
from ipaddress import IPv4Address, IPv6Address
from typing import Any, cast

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .api import KioskerApiClient
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_BASE_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .exceptions import (
    KioskerConnectionError,
    KioskerInvalidAuth,
    KioskerUnexpectedResponse,
)

_LOGGER = logging.getLogger(__name__)

_ACCESS_TOKEN_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
)
_DEFAULT_API_PORT = 8081


def _decode_zeroconf_value(value: Any) -> str:
    """Normalize zeroconf property values into strings."""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value)


def _normalize_zeroconf_properties(
    properties: dict[str, Any],
) -> dict[str, str]:
    """Return lowercase string keys with decoded string values."""
    normalized: dict[str, str] = {}
    for key, value in properties.items():
        key_str = _decode_zeroconf_value(key).lower()
        normalized[key_str] = _decode_zeroconf_value(value)
    return normalized


def _name_from_hostname(hostname: str) -> str:
    """Convert a hostname to a user-friendly name."""
    name = hostname.rstrip(".")
    if name.endswith(".local"):
        name = name[: -len(".local")]
    return name


def _select_ip_address(
    discovery_info: ZeroconfServiceInfo,
) -> IPv4Address | IPv6Address:
    """Prefer IPv4 when available; fall back to the primary zeroconf address."""
    for address in discovery_info.ip_addresses:
        if (
            isinstance(address, IPv4Address)
            and not address.is_link_local
            and not address.is_unspecified
        ):
            return address
    return discovery_info.ip_address


def _build_base_url(ip_address: IPv4Address | IPv6Address, port: int | None) -> str:
    """Build the Kiosker base URL from zeroconf details."""
    host = str(ip_address)
    if isinstance(ip_address, IPv6Address):
        host = f"[{host}]"
    return f"http://{host}:{port or _DEFAULT_API_PORT}/api/v1"


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
    _discovered_base_url: str | None = None
    _discovered_name: str | None = None
    _discovered_uuid: str | None = None

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_BASE_URL] = user_input[CONF_BASE_URL].strip().rstrip("/")
            user_input[CONF_ACCESS_TOKEN] = user_input[CONF_ACCESS_TOKEN].strip()
            try:
                status = await _validate_input(self.hass, user_input)
            except KioskerInvalidAuth:
                _LOGGER.error(
                    "Kiosker config flow: invalid auth for %s",
                    user_input[CONF_BASE_URL],
                )
                errors["base"] = "invalid_auth"
            except KioskerConnectionError as err:
                _LOGGER.error(
                    "Kiosker config flow: cannot connect to %s (%s)",
                    user_input[CONF_BASE_URL],
                    err,
                )
                errors["base"] = "cannot_connect"
            except KioskerUnexpectedResponse as err:
                _LOGGER.error(
                    "Kiosker config flow: unexpected response for %s (%s)",
                    user_input[CONF_BASE_URL],
                    err,
                )
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
                vol.Required(
                    CONF_BASE_URL,
                    description={"suggested_value": "http://ipad-ip:8081/api/v1"},
                ): str,
                vol.Required(CONF_ACCESS_TOKEN): _ACCESS_TOKEN_SELECTOR,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        properties = _normalize_zeroconf_properties(discovery_info.properties)
        uuid = properties.get("uuid")
        if not uuid:
            _LOGGER.error(
                "Kiosker zeroconf discovery missing uuid for %s",
                discovery_info.name,
            )
            return self.async_abort(reason="missing_uuid")

        self._discovered_uuid = uuid
        await self.async_set_unique_id(uuid)

        ip_address = _select_ip_address(discovery_info)
        base_url = _build_base_url(ip_address, discovery_info.port).rstrip("/")
        self._discovered_base_url = base_url

        name = _name_from_hostname(discovery_info.hostname)
        self._discovered_name = name or properties.get("app") or uuid

        self.context["title_placeholders"] = {
            "name": self._discovered_name or DEFAULT_NAME
        }

        self._abort_if_unique_id_configured(updates={CONF_BASE_URL: base_url})

        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Confirm zeroconf discovery and collect the access token."""
        if not self._discovered_base_url or not self._discovered_uuid:
            _LOGGER.error("Kiosker zeroconf confirm missing discovery context")
            return self.async_abort(reason="missing_discovery")

        errors: dict[str, str] = {}
        if user_input is not None:
            access_token = user_input[CONF_ACCESS_TOKEN].strip()
            data = {
                CONF_BASE_URL: self._discovered_base_url,
                CONF_ACCESS_TOKEN: access_token,
            }
            try:
                status = await _validate_input(self.hass, data)
            except KioskerInvalidAuth:
                _LOGGER.error(
                    "Kiosker zeroconf config flow: invalid auth for %s",
                    self._discovered_base_url,
                )
                errors["base"] = "invalid_auth"
            except KioskerConnectionError as err:
                _LOGGER.error(
                    "Kiosker zeroconf config flow: cannot connect to %s (%s)",
                    self._discovered_base_url,
                    err,
                )
                errors["base"] = "cannot_connect"
            except KioskerUnexpectedResponse as err:
                _LOGGER.error(
                    "Kiosker zeroconf config flow: unexpected response for %s (%s)",
                    self._discovered_base_url,
                    err,
                )
                errors["base"] = "unknown"
            else:
                self._abort_if_unique_id_configured()

                title = (
                    self._discovered_name
                    or status.app_name
                    or f"{DEFAULT_NAME} {status.device_id}"
                )
                entry_data = {
                    CONF_BASE_URL: self._discovered_base_url,
                    CONF_ACCESS_TOKEN: access_token,
                }
                return self.async_create_entry(title=title, data=entry_data)

        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=vol.Schema(
                {vol.Required(CONF_ACCESS_TOKEN): _ACCESS_TOKEN_SELECTOR}
            ),
            errors=errors,
            description_placeholders={"name": self._discovered_name or DEFAULT_NAME},
        )

    async def async_step_reauth(
        self, _entry_data: dict[str, str]
    ) -> ConfigFlowResult:  # pragma: no cover - exercised in HA runtime
        """Handle reauthentication."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauthentication."""
        if self._reauth_entry is None:
            _LOGGER.error("Kiosker reauth: missing entry in context")
            return self.async_abort(reason="reauth_failed")
        errors: dict[str, str] = {}

        if user_input is not None:
            update = {
                **self._reauth_entry.data,
                CONF_ACCESS_TOKEN: user_input[CONF_ACCESS_TOKEN],
            }
            try:
                await _validate_input(self.hass, update)
            except KioskerInvalidAuth:
                _LOGGER.error(
                    "Kiosker reauth: invalid auth for %s", update[CONF_BASE_URL]
                )
                errors["base"] = "invalid_auth"
            except KioskerConnectionError as err:
                _LOGGER.error(
                    "Kiosker reauth: cannot connect to %s (%s)",
                    update[CONF_BASE_URL],
                    err,
                )
                errors["base"] = "cannot_connect"
            except KioskerUnexpectedResponse as err:
                _LOGGER.error(
                    "Kiosker reauth: unexpected response for %s (%s)",
                    update[CONF_BASE_URL],
                    err,
                )
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry, data=update
                )
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {vol.Required(CONF_ACCESS_TOKEN): _ACCESS_TOKEN_SELECTOR}
            ),
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
            return cast(FlowResult, self.async_create_entry(title="", data=user_input))

        current_interval = self.entry.options.get(
            CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds())
        )
        current_interval = max(
            min(current_interval, int(MAX_SCAN_INTERVAL.total_seconds())),
            int(MIN_SCAN_INTERVAL.total_seconds()),
        )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_interval,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(
                        min=int(MIN_SCAN_INTERVAL.total_seconds()),
                        max=int(MAX_SCAN_INTERVAL.total_seconds()),
                    ),
                ),
            }
        )

        return cast(
            FlowResult,
            self.async_show_form(
                step_id="init",
                data_schema=data_schema,
                errors={},
            ),
        )
