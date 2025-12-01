"""Custom exceptions for the Kiosker integration."""

from __future__ import annotations


class KioskerError(Exception):
    """Base error for Kiosker integration."""


class KioskerConnectionError(KioskerError):
    """Raised when the API cannot be reached."""


class KioskerInvalidAuth(KioskerError):
    """Raised when authentication fails."""


class KioskerUnexpectedResponse(KioskerError):
    """Raised when the API returns unexpected data."""
