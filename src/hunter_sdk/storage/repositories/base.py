"""Repository protocol describing CRUD operations on verification records."""

from typing import Any, Mapping, Protocol
from uuid import UUID

from hunter_sdk.storage.entities import NewVerification, VerificationRecord


class VerificationRepository(Protocol):
    """CRUD interface for stored Hunter.io verifications."""

    async def create(self, record: NewVerification) -> VerificationRecord:
        """Persist a new verification and return the stored record."""

    async def get(self, record_id: UUID) -> VerificationRecord | None:
        """Return a single record by id or ``None`` when missing."""

    async def list_all(self, *, limit: int = 50, offset: int = 0) -> list[VerificationRecord]:
        """List records ordered by ``created_at`` descending."""

    async def update(
        self,
        record_id: UUID,
        *,
        response: Mapping[str, Any],
    ) -> VerificationRecord | None:
        """Replace the stored response and return the updated record."""

    async def delete(self, record_id: UUID) -> bool:
        """Delete a record. Return ``True`` when a row was removed."""
