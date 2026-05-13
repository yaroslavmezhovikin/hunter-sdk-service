"""Verification service: orchestrates Hunter.io endpoints and persistence.

Pure CRUD on stored records lives on the repository — the service only
exists to combine an outbound API call with persistence of its result.
"""

from typing import Final

from hunter_sdk.sdk.endpoints.domain_search import DomainSearch
from hunter_sdk.sdk.endpoints.email_finder import EmailFinder
from hunter_sdk.sdk.endpoints.email_verifier import EmailVerifier
from hunter_sdk.sdk.transport import HunterTransport
from hunter_sdk.storage.entities import NewVerification, VerificationRecord
from hunter_sdk.storage.repositories.base import VerificationRepository

OPERATION_VERIFY_EMAIL: Final[str] = 'verify_email'
OPERATION_FIND_EMAIL: Final[str] = 'find_email'
OPERATION_DOMAIN_SEARCH: Final[str] = 'domain_search'


class VerificationService:
    """Calls a Hunter.io endpoint, then persists the result via the repository."""

    def __init__(
        self,
        transport: HunterTransport,
        repository: VerificationRepository,
    ) -> None:
        """Wire the service to a transport and a repository."""
        self._repository = repository
        self._email_verifier = EmailVerifier(transport)
        self._email_finder = EmailFinder(transport)
        self._domain_search = DomainSearch(transport)

    async def verify_email(self, email: str) -> VerificationRecord:
        """Verify ``email`` and persist the response."""
        verification = await self._email_verifier(email=email)
        return await self._repository.create(NewVerification(
            operation=OPERATION_VERIFY_EMAIL,
            query={'email': email},
            response=verification.model_dump(),
        ))

    async def find_email(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> VerificationRecord:
        """Find an email for ``first_name last_name`` at ``domain`` and persist it."""
        finding = await self._email_finder(
            domain=domain,
            first_name=first_name,
            last_name=last_name,
        )
        return await self._repository.create(NewVerification(
            operation=OPERATION_FIND_EMAIL,
            query={'domain': domain, 'first_name': first_name, 'last_name': last_name},
            response=finding.model_dump(),
        ))

    async def search_domain(self, domain: str) -> VerificationRecord:
        """Search public emails for ``domain`` and persist the response."""
        search_result = await self._domain_search(domain=domain)
        return await self._repository.create(NewVerification(
            operation=OPERATION_DOMAIN_SEARCH,
            query={'domain': domain},
            response=search_result.model_dump(),
        ))
