"""High-level verification service: calls the SDK and stores the result."""

from typing import Any, Final, Mapping
from uuid import UUID

from hunter_sdk.sdk.client import HunterClient
from hunter_sdk.storage.entities import NewVerification, VerificationRecord
from hunter_sdk.storage.repositories.base import VerificationRepository

OPERATION_VERIFY_EMAIL: Final[str] = 'verify_email'
OPERATION_FIND_EMAIL: Final[str] = 'find_email'
OPERATION_DOMAIN_SEARCH: Final[str] = 'domain_search'


class VerificationService:
    """Orchestrates Hunter.io API calls and persistence of their results."""

    def __init__(
        self,
        sdk: HunterClient,
        repository: VerificationRepository,
    ) -> None:
        """Bind the service to an SDK client and a repository."""
        self._sdk = sdk
        self._repository = repository

    async def verify_email(self, email: str) -> VerificationRecord:
        """Verify ``email`` and persist the response."""
        verification = await self._sdk.verify_email(email)
        return await self._persist(
            OPERATION_VERIFY_EMAIL,
            {'email': email},
            verification.model_dump(),
        )

    async def find_email(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> VerificationRecord:
        """Find an email for ``first_name last_name`` at ``domain`` and persist it."""
        finding = await self._sdk.find_email(domain, first_name, last_name)
        return await self._persist(
            OPERATION_FIND_EMAIL,
            {'domain': domain, 'first_name': first_name, 'last_name': last_name},
            finding.model_dump(),
        )

    async def search_domain(self, domain: str) -> VerificationRecord:
        """Search public emails for ``domain`` and persist the response."""
        search = await self._sdk.search_domain(domain)
        return await self._persist(
            OPERATION_DOMAIN_SEARCH,
            {'domain': domain},
            search.model_dump(),
        )

    async def get(self, record_id: UUID) -> VerificationRecord | None:
        """Return a single stored verification."""
        return await self._repository.get(record_id)

    async def list_all(self, *, limit: int = 50, offset: int = 0) -> list[VerificationRecord]:
        """List stored verifications."""
        return await self._repository.list_all(limit=limit, offset=offset)

    async def delete(self, record_id: UUID) -> bool:
        """Delete a stored verification."""
        return await self._repository.delete(record_id)

    async def _persist(
        self,
        operation: str,
        query: Mapping[str, Any],
        response: Mapping[str, Any],
    ) -> VerificationRecord:
        return await self._repository.create(
            NewVerification(operation=operation, query=query, response=response),
        )
