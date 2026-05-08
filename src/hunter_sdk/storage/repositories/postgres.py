"""PostgreSQL-backed repository using SQLAlchemy 2.0 async sessions."""

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hunter_sdk.storage.entities import NewVerification, VerificationRecord
from hunter_sdk.storage.orm import VerificationRow


def _to_entity(row: VerificationRow) -> VerificationRecord:
    return VerificationRecord(
        record_id=row.record_id,
        operation=row.operation,
        query=dict(row.query),
        response=dict(row.response),
        created_at=row.created_at,
    )


class PostgresVerificationRepository:
    """Async CRUD repository backed by SQLAlchemy and PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to an existing async session."""
        self._session = session

    async def create(self, record: NewVerification) -> VerificationRecord:
        """Insert a new row and return the persisted record."""
        row = VerificationRow(
            record_id=uuid4(),
            operation=record.operation,
            query=dict(record.query),
            response=dict(record.response),
            created_at=datetime.now(tz=timezone.utc),
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.commit()
        return _to_entity(row)

    async def get(self, record_id: UUID) -> VerificationRecord | None:
        """Return a single row by primary key."""
        row = await self._session.get(VerificationRow, record_id)
        if row is None:
            return None
        return _to_entity(row)

    async def list_all(self, *, limit: int = 50, offset: int = 0) -> list[VerificationRecord]:
        """List rows ordered by ``created_at`` descending."""
        statement = (
            select(VerificationRow)
            .order_by(VerificationRow.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self._session.execute(statement)).scalars().all()
        return [_to_entity(row) for row in rows]

    async def update(
        self,
        record_id: UUID,
        *,
        response: Mapping[str, Any],
    ) -> VerificationRecord | None:
        """Replace the stored response of an existing row."""
        row = await self._session.get(VerificationRow, record_id)
        if row is None:
            return None
        row.response = dict(response)
        await self._session.flush()
        await self._session.commit()
        return _to_entity(row)

    async def delete(self, record_id: UUID) -> bool:
        """Delete a row by id."""
        row = await self._session.get(VerificationRow, record_id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.commit()
        return True
