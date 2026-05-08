"""Request and response schemas exposed by the FastAPI layer."""

from datetime import datetime
from typing import Any, Final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from hunter_sdk.storage.entities import VerificationRecord

_DOMAIN_MAX_LENGTH: Final[int] = 253
_NAME_MAX_LENGTH: Final[int] = 64


class VerifyEmailRequest(BaseModel):
    """Body of ``POST /verifications/email``."""

    email: EmailStr


class FindEmailRequest(BaseModel):
    """Body of ``POST /verifications/find``."""

    domain: str = Field(..., min_length=1, max_length=_DOMAIN_MAX_LENGTH)
    first_name: str = Field(..., min_length=1, max_length=_NAME_MAX_LENGTH)
    last_name: str = Field(..., min_length=1, max_length=_NAME_MAX_LENGTH)


class DomainSearchRequest(BaseModel):
    """Body of ``POST /verifications/domain``."""

    domain: str = Field(..., min_length=1, max_length=_DOMAIN_MAX_LENGTH)


class VerificationResponse(BaseModel):
    """Public representation of a stored verification."""

    model_config = ConfigDict(from_attributes=True)

    record_id: UUID
    operation: str
    query: dict[str, Any]
    response: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_entity(cls, record: VerificationRecord) -> 'VerificationResponse':
        """Build a response model from a stored entity."""
        return cls(
            record_id=record.record_id,
            operation=record.operation,
            query=dict(record.query),
            response=dict(record.response),
            created_at=record.created_at,
        )
