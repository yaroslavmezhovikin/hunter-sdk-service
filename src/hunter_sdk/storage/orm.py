"""SQLAlchemy ORM models for persisted Hunter.io verifications."""

import uuid
from datetime import datetime, timezone
from typing import Any, Final

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

_OPERATION_MAX_LENGTH: Final[int] = 64


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class Base(DeclarativeBase):
    """Declarative base for all ORM models in this project."""


class VerificationRow(Base):
    """ORM mapping for the ``verifications`` table."""

    __tablename__ = 'verifications'

    record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    operation: Mapped[str] = mapped_column(
        String(_OPERATION_MAX_LENGTH),
        nullable=False,
        index=True,
    )
    query: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    response: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
