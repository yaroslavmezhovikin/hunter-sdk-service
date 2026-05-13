"""Domain search endpoint: ``GET /v2/domain-search``."""

from typing import ClassVar

from hunter_sdk.sdk.models import DomainSearchResult
from hunter_sdk.sdk.transport import HunterTransport


class DomainSearch:
    """List public emails attributed to a domain."""

    path: ClassVar[str] = '/v2/domain-search'

    def __init__(self, transport: HunterTransport) -> None:
        """Bind the endpoint to a shared transport."""
        self._transport = transport

    async def __call__(self, *, domain: str) -> DomainSearchResult:
        """Return public emails and organisation metadata for ``domain``."""
        record = await self._transport.get(self.path, {'domain': domain})
        return DomainSearchResult.model_validate(record)
