"""Pydantic models describing Hunter.io API response payloads."""

from pydantic import BaseModel, ConfigDict, Field


class _HunterModel(BaseModel):
    """Base model that ignores unknown Hunter.io response fields."""

    model_config = ConfigDict(populate_by_name=True, extra='ignore')


class EmailVerification(_HunterModel):
    """Result of the ``/v2/email-verifier`` endpoint."""

    email: str
    status: str
    score: int = 0
    regexp: bool | None = None
    gibberish: bool | None = None
    disposable: bool | None = None
    webmail: bool | None = None
    mx_records: bool | None = None
    smtp_server: bool | None = None
    smtp_check: bool | None = None
    accept_all: bool | None = None
    block: bool | None = None


class EmailFinding(_HunterModel):
    """Result of the ``/v2/email-finder`` endpoint."""

    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    score: int | None = None
    domain: str | None = None
    position: str | None = None
    company: str | None = None


class DomainEmail(_HunterModel):
    """Single email entry within a domain search response."""

    email_address: str = Field(alias='value')
    email_type: str | None = Field(default=None, alias='type')
    confidence: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    position: str | None = None


class DomainSearchResult(_HunterModel):
    """Result of the ``/v2/domain-search`` endpoint."""

    domain: str
    organization: str | None = None
    country: str | None = None
    emails: list[DomainEmail] = Field(default_factory=list)
