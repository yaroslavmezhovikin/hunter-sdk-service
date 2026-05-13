"""Email finder endpoint: ``GET /v2/email-finder``."""

from typing import ClassVar

from hunter_sdk.sdk.models import EmailFinding
from hunter_sdk.sdk.transport import HunterTransport


class EmailFinder:
    """Find the most likely email for a person at a given domain."""

    path: ClassVar[str] = '/v2/email-finder'

    def __init__(self, transport: HunterTransport) -> None:
        """Bind the endpoint to a shared transport."""
        self._transport = transport

    async def __call__(
        self,
        *,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> EmailFinding:
        """Return the best-guess email for ``first_name last_name`` at ``domain``."""
        record = await self._transport.get(
            self.path,
            {'domain': domain, 'first_name': first_name, 'last_name': last_name},
        )
        return EmailFinding.model_validate(record)
