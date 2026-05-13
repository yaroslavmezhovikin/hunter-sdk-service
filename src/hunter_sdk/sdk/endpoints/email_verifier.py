"""Email verifier endpoint: ``GET /v2/email-verifier``."""

from typing import ClassVar

from hunter_sdk.sdk.models import EmailVerification
from hunter_sdk.sdk.transport import HunterTransport


class EmailVerifier:
    """Verify a single email address via the Hunter.io API."""

    path: ClassVar[str] = '/v2/email-verifier'

    def __init__(self, transport: HunterTransport) -> None:
        """Bind the endpoint to a shared transport."""
        self._transport = transport

    async def __call__(self, *, email: str) -> EmailVerification:
        """Return the deliverability verdict for ``email``."""
        record = await self._transport.get(self.path, {'email': email})
        return EmailVerification.model_validate(record)
