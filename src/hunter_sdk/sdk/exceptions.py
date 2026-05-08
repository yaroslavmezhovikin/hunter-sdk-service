"""Exceptions raised by the Hunter.io SDK client."""


class HunterError(Exception):
    """Base error for the Hunter SDK."""


class HunterTimeoutError(HunterError):
    """Raised when an HTTP request to Hunter.io times out."""


class HunterAPIError(HunterError):
    """Raised when Hunter.io returns a non-2xx response."""

    def __init__(self, status_code: int, message: str) -> None:
        """Store the HTTP status code alongside the error message."""
        super().__init__(message)
        self.status_code = status_code
        self.message = message
