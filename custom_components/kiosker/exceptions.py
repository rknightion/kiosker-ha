"""Custom exceptions for the Kiosker integration."""

from __future__ import annotations


class KioskerError(Exception):
    """Base error for Kiosker integration."""


class KioskerConnectionError(KioskerError):
    """Raised when the API cannot be reached."""


class KioskerInvalidAuth(KioskerError):  # noqa: N818
    """Raised when authentication fails."""


class KioskerUnexpectedResponse(KioskerError):  # noqa: N818
    """Raised when the API returns unexpected data."""
