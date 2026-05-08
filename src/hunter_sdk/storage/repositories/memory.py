"""In-memory dictionary repository — useful for tests and the sandbox demo."""

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID

from hunter_sdk.storage.entities import NewVerification, VerificationRecord, new_record


class InMemoryVerificationRepository:
    """Stores verifications in a plain ``dict``. Not thread-safe."""

    def __init__(self) -> None:
        """Initialise an empty store."""
        self._store: dict[UUID, VerificationRecord] = {}

    async def create(self, record: NewVerification) -> VerificationRecord:
        """Persist a new verification."""
        stored = new_record(record, datetime.now(tz=timezone.utc))
        self._store[stored.record_id] = stored
        return stored

    async def get(self, record_id: UUID) -> VerificationRecord | None:
        """Return a record by id or ``None``."""
        return self._store.get(record_id)

    async def list_all(self, *, limit: int = 50, offset: int = 0) -> list[VerificationRecord]:
        """Return records ordered by ``created_at`` descending."""
        ordered = sorted(
            self._store.values(),
            key=lambda stored: stored.created_at,
            reverse=True,
        )
        return ordered[offset:offset + limit]

    async def update(
        self,
        record_id: UUID,
        *,
        response: Mapping[str, Any],
    ) -> VerificationRecord | None:
        """Replace the response payload of an existing record."""
        existing = self._store.get(record_id)
        if existing is None:
            return None
        replaced = VerificationRecord(
            record_id=existing.record_id,
            operation=existing.operation,
            query=existing.query,
            response=dict(response),
            created_at=existing.created_at,
        )
        self._store[record_id] = replaced
        return replaced

    async def delete(self, record_id: UUID) -> bool:
        """Delete a record by id. Return ``True`` if it existed."""
        return self._store.pop(record_id, None) is not None
