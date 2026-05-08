"""Asynchronous Hunter.io API client."""

from types import TracebackType
from typing import Any, Final, Mapping

import httpx

from hunter_sdk.sdk.exceptions import HunterAPIError, HunterTimeoutError
from hunter_sdk.sdk.models import DomainSearchResult, EmailFinding, EmailVerification

_VERIFIER_PATH: Final[str] = '/v2/email-verifier'
_FINDER_PATH: Final[str] = '/v2/email-finder'
_DOMAIN_PATH: Final[str] = '/v2/domain-search'

_HTTP_BAD_REQUEST: Final[int] = 400


class HunterClient:
    """Async client wrapping a small subset of the Hunter.io REST API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = 'https://api.hunter.io',
        timeout: float = 10.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Create a client. Pass ``http_client`` to share an external session."""
        self._api_key = api_key
        self._base_url = base_url.rstrip('/')
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> 'HunterClient':
        """Enter an async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the underlying HTTP client when leaving the context."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the HTTP client if it was created internally."""
        if self._owns_client:
            await self._client.aclose()

    async def verify_email(self, email: str) -> EmailVerification:
        """Verify a single email address."""
        record = await self._get(_VERIFIER_PATH, {'email': email})
        return EmailVerification.model_validate(record)

    async def find_email(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> EmailFinding:
        """Find the most likely email for a person at a given domain."""
        record = await self._get(
            _FINDER_PATH,
            {'domain': domain, 'first_name': first_name, 'last_name': last_name},
        )
        return EmailFinding.model_validate(record)

    async def search_domain(self, domain: str) -> DomainSearchResult:
        """List public emails attributed to a domain."""
        record = await self._get(_DOMAIN_PATH, {'domain': domain})
        return DomainSearchResult.model_validate(record)

    async def _get(
        self,
        path: str,
        query: Mapping[str, str],
    ) -> Mapping[str, Any]:
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
