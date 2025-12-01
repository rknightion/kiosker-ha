"""API client for the Kiosker integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout
from yarl import URL

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.util import dt as dt_util

from .const import REQUEST_TIMEOUT
from .exceptions import (
    KioskerConnectionError,
    KioskerInvalidAuth,
    KioskerUnexpectedResponse,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceStatus:
    """Representation of the kiosk status payload."""

    device_id: str
    app_version: str | None
    app_name: str | None
    os_version: str | None
    model: str | None
    date: datetime | None
    ambient_light: float | None
    battery_level: int | None
    battery_state: str | None
    last_interaction: datetime | None
    last_motion: datetime | None


@dataclass
class ScreensaverState:
    """Screensaver state details."""

    visible: bool | None
    disabled: bool | None


@dataclass
class BlackoutState:
    """Blackout state details."""

    visible: bool | None
    text: str | None
    background: str | None
    foreground: str | None
    icon: str | None
    expire: int | None


class KioskerApiClient:
    """Handle communication with the Kiosker API."""

    def __init__(self, hass: HomeAssistant, base_url: str, access_token: str) -> None:
        """Initialize the client."""
        self._hass = hass
        self._base_url = URL(base_url.rstrip("/"))
        self._access_token = access_token

    async def _request(
        self, method: str, path: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make an authenticated request against the Kiosker API."""
        url = self._base_url / path.lstrip("/")
        aiohttp_session = aiohttp_client.async_get_clientsession(self._hass)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
        }

        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                _LOGGER.debug("Kiosker request %s %s", method, url)
                async with aiohttp_session.request(
                    method,
                    url,
                    json=json,
                    headers=headers,
                ) as response:
                    if response.status == 401:
                        _LOGGER.debug("Kiosker auth failed for %s %s", method, url)
                        raise KioskerInvalidAuth("Authentication failed")
                    if response.status in (403, 404):
                        raise KioskerUnexpectedResponse(
                            f"Unexpected status from Kiosker: {response.status}"
                        )
                    text = await response.text()
                    try:
                        payload: dict[str, Any] = await response.json(content_type=None)
                    except Exception:
                        _LOGGER.error(
                            "Kiosker response JSON decode failed status=%s url=%s body=%s",
                            response.status,
                            url,
                            text,
                        )
                        raise KioskerUnexpectedResponse(
                            f"Invalid JSON from Kiosker: {text}"
                        ) from None
                    if response.status >= 400:
                        _LOGGER.error(
                            "Kiosker HTTP error status=%s url=%s payload=%s body=%s",
                            response.status,
                            url,
                            payload,
                            text,
                        )
                        raise KioskerUnexpectedResponse(
                            f"HTTP {response.status}: {payload.get('reason') or payload}"
                        )
                    _LOGGER.debug(
                        "Kiosker response %s %s status=%s payload=%s body=%s",
                        method,
                        url,
                        response.status,
                        payload,
                        text,
                    )
        except aiohttp.ClientResponseError as err:
            _LOGGER.error("Kiosker client response error: %s", err)
            raise KioskerUnexpectedResponse(err.message) from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Kiosker client error: %s", err)
            raise KioskerConnectionError(err) from err
        except asyncio.TimeoutError as err:
            _LOGGER.error("Kiosker request timeout: %s", err)
            raise KioskerConnectionError(err) from err

        if payload.get("error") is True:
            _LOGGER.error("Kiosker API returned error payload: %s", payload)
            raise KioskerUnexpectedResponse(payload.get("reason") or "API error")

        return payload

    def _parse_status(self, data: dict[str, Any]) -> DeviceStatus:
        """Parse the status payload into a DeviceStatus object."""
        status: dict[str, Any] = data.get("status") or {}
        device_id = status.get("deviceId")
        if not device_id:
            raise KioskerUnexpectedResponse("Missing deviceId in status response")

        return DeviceStatus(
            device_id=device_id,
            app_version=status.get("appVersion"),
            app_name=status.get("appName"),
            os_version=status.get("osVersion"),
            model=status.get("model"),
            date=dt_util.parse_datetime(status["date"]) if status.get("date") else None,
            ambient_light=_to_float(status.get("ambientLight")),
            battery_level=_to_int(status.get("batteryLevel")),
            battery_state=status.get("batteryState"),
            last_interaction=dt_util.parse_datetime(status["lastInteraction"])
            if status.get("lastInteraction")
            else None,
            last_motion=dt_util.parse_datetime(status["lastMotion"])
            if status.get("lastMotion")
            else None,
        )

    @staticmethod
    def _parse_screensaver(data: dict[str, Any]) -> ScreensaverState | None:
        """Parse a screensaver state response."""
        payload = data.get("screensaver")
        if payload is None:
            return None
        return ScreensaverState(
            visible=payload.get("visible"),
            disabled=payload.get("disabled"),
        )

    @staticmethod
    def _parse_blackout(data: dict[str, Any]) -> BlackoutState | None:
        """Parse a blackout state response."""
        payload = data.get("blackout")
        if payload is None:
            return None
        return BlackoutState(
            visible=payload.get("visible"),
            text=payload.get("text"),
            background=payload.get("background"),
            foreground=payload.get("foreground"),
            icon=payload.get("icon"),
            expire=payload.get("expire"),
        )

    async def async_get_status(self) -> DeviceStatus:
        """Fetch the current kiosk status."""
        payload = await self._request("GET", "status")
        return self._parse_status(payload)

    async def async_get_screensaver_state(self) -> ScreensaverState | None:
        """Fetch the screensaver state."""
        payload = await self._request("GET", "screensaver/state")
        return self._parse_screensaver(payload)

    async def async_get_blackout_state(self) -> BlackoutState | None:
        """Fetch the blackout state."""
        payload = await self._request("GET", "blackout/state")
        return self._parse_blackout(payload)

    async def async_ping(self) -> None:
        """Ping the kiosk to verify connectivity."""
        await self._request("GET", "ping")

    async def async_print(self) -> None:
        """Trigger a print of the current page."""
        await self._request("POST", "print")

    async def async_clear_cache(self) -> None:
        """Clear browser cache and data."""
        await self._request("POST", "clear/cache")

    async def async_clear_cookies(self) -> None:
        """Clear cookies."""
        await self._request("POST", "clear/cookies")

    async def async_navigate_home(self) -> None:
        """Navigate to the start page."""
        await self._request("POST", "navigate/home")

    async def async_navigate_refresh(self) -> None:
        """Refresh the current website."""
        await self._request("POST", "navigate/refresh")

    async def async_navigate_forward(self) -> None:
        """Navigate forward in history."""
        await self._request("POST", "navigate/forward")

    async def async_navigate_backward(self) -> None:
        """Navigate backward in history."""
        await self._request("POST", "navigate/backward")

    async def async_navigate_url(self, url: str) -> None:
        """Navigate to a specific URL."""
        await self._request("POST", "navigate/url", json={"url": url})

    async def async_screensaver_interact(self) -> None:
        """Simulate interaction to dismiss screensaver."""
        await self._request("POST", "screensaver/interact")

    async def async_set_screensaver(
        self, disabled: bool, visible: bool | None = None
    ) -> None:
        """Set screensaver state."""
        payload: dict[str, Any] = {"disabled": disabled}
        if visible is not None:
            payload["visible"] = visible
        try:
            await self._request("POST", "devices/screensaver", json=payload)
        except KioskerUnexpectedResponse:
            await self._request("POST", "screensaver/state", json=payload)

    async def async_set_blackout(
        self,
        visible: bool,
        text: str | None = None,
        background: str | None = None,
        foreground: str | None = None,
        icon: str | None = None,
        expire: int | None = None,
    ) -> None:
        """Set blackout state."""
        payload: dict[str, Any] = {"visible": visible}
        if text is not None:
            payload["text"] = text
        if background is not None:
            payload["background"] = background
        if foreground is not None:
            payload["foreground"] = foreground
        if icon is not None:
            payload["icon"] = icon
        if expire is not None:
            payload["expire"] = expire
        try:
            await self._request("POST", "devices/blackout", json=payload)
        except KioskerUnexpectedResponse:
            # Older API versions expose /blackout instead of /devices/blackout
            await self._request("POST", "blackout", json=payload)

    async def async_set_start_url(self, url: str) -> None:
        """Set the device default URL."""
        try:
            await self._request("POST", "devices/url", json={"url": url})
        except KioskerUnexpectedResponse:
            await self._request("POST", "navigate/url", json={"url": url})


def _to_int(value: Any) -> int | None:
    """Attempt to cast value to int."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> float | None:
    """Attempt to cast value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
