"""HTTP transport for the Hunter.io API.

The transport is intentionally tiny: it owns the base URL, attaches the
API key, performs a GET and translates transport-level failures into the
SDK's own exceptions. Every endpoint object reuses one transport
instance — none of them need their own HTTP logic.
"""

from types import TracebackType
from typing import Any, Final, Mapping

import httpx

from hunter_sdk.sdk.exceptions import HunterAPIError, HunterTimeoutError

_HTTP_BAD_REQUEST: Final[int] = 400
_DEFAULT_TIMEOUT_SECONDS: Final[float] = 10.0


class HunterTransport:
    """Async HTTP transport for the Hunter.io REST API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = 'https://api.hunter.io',
        timeout: float = _DEFAULT_TIMEOUT_SECONDS,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Bind the transport to an API key and optional shared ``http_client``."""
        self._api_key = api_key
        self._base_url = base_url.rstrip('/')
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> 'HunterTransport':
        """Enter an async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the underlying HTTP client on exit."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the HTTP client if it was created internally."""
        if self._owns_client:
            await self._client.aclose()

    async def get(
        self,
        path: str,
        query: Mapping[str, str],
    ) -> Mapping[str, Any]:
        """Perform a GET, validate the response and return the ``data`` payload."""
        request_query = {**query, 'api_key': self._api_key}
        url = '{0}{1}'.format(self._base_url, path)
        try:
            response = await self._client.get(url, params=request_query)
        except httpx.TimeoutException as timeout_exc:
            raise HunterTimeoutError(str(timeout_exc)) from timeout_exc
        if response.status_code >= _HTTP_BAD_REQUEST:
            raise HunterAPIError(response.status_code, response.text)
        body: Mapping[str, Any] = response.json()
        record = body.get('data')
        if not isinstance(record, Mapping):
            return {}
        return record
