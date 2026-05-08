"""Plain domain entities exchanged between repositories and the service layer."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class NewVerification:
    """Inbound payload describing a verification to persist."""

    operation: str
    query: Mapping[str, Any]
    response: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class VerificationRecord:
    """Stored representation of a single Hunter.io verification."""

    record_id: UUID
    operation: str
    query: Mapping[str, Any]
    response: Mapping[str, Any]
    created_at: datetime


def new_record(record: NewVerification, now: datetime) -> VerificationRecord:
    """Materialise a ``NewVerification`` into a stored ``VerificationRecord``."""
    return VerificationRecord(
        record_id=uuid4(),
        operation=record.operation,
        query=dict(record.query),
        response=dict(record.response),
        created_at=now,
    )
