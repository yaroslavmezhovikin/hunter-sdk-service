"""HTTP endpoints exposing verification operations and stored records.

Operations that need the Hunter.io API go through ``VerificationService``;
pure storage queries (list / get / delete) go straight to the repository.
"""

from typing import Annotated, Final
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status

from hunter_sdk.api.dependencies import RepositoryDep, ServiceDep
from hunter_sdk.api.schemas import DomainSearchRequest, FindEmailRequest, VerificationResponse, VerifyEmailRequest
from hunter_sdk.sdk.exceptions import HunterAPIError, HunterTimeoutError

router = APIRouter(prefix='/verifications', tags=['verifications'])

_MAX_PAGE_SIZE: Final[int] = 200
_DEFAULT_PAGE_SIZE: Final[int] = 50

LimitQuery = Annotated[int, Query(gt=0, le=_MAX_PAGE_SIZE)]
OffsetQuery = Annotated[int, Query(ge=0)]


def _translate_sdk_errors(exc: Exception) -> HTTPException:
    if isinstance(exc, HunterTimeoutError):
        return HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc))
    if isinstance(exc, HunterAPIError):
        return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message)
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post(
    '/email',
    response_model=VerificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def verify_email_endpoint(
    body: VerifyEmailRequest,
    service: ServiceDep,
) -> VerificationResponse:
    """Verify an email address and persist the result."""
    try:
        record = await service.verify_email(body.email)
    except (HunterAPIError, HunterTimeoutError) as sdk_exc:
        raise _translate_sdk_errors(sdk_exc) from sdk_exc
    return VerificationResponse.from_entity(record)


@router.post(
    '/find',
    response_model=VerificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def find_email_endpoint(
    body: FindEmailRequest,
    service: ServiceDep,
) -> VerificationResponse:
    """Find an email for a person at a given domain and persist the result."""
    try:
        record = await service.find_email(body.domain, body.first_name, body.last_name)
    except (HunterAPIError, HunterTimeoutError) as sdk_exc:
        raise _translate_sdk_errors(sdk_exc) from sdk_exc
    return VerificationResponse.from_entity(record)


@router.post(
    '/domain',
    response_model=VerificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def search_domain_endpoint(
    body: DomainSearchRequest,
    service: ServiceDep,
) -> VerificationResponse:
    """Search public emails for a domain and persist the result."""
    try:
        record = await service.search_domain(body.domain)
    except (HunterAPIError, HunterTimeoutError) as sdk_exc:
        raise _translate_sdk_errors(sdk_exc) from sdk_exc
    return VerificationResponse.from_entity(record)


@router.get('', response_model=list[VerificationResponse])
async def list_verifications_endpoint(
    repository: RepositoryDep,
    limit: LimitQuery = _DEFAULT_PAGE_SIZE,
    offset: OffsetQuery = 0,
) -> list[VerificationResponse]:
    """List stored verifications, newest first."""
    records = await repository.list_all(limit=limit, offset=offset)
    return [VerificationResponse.from_entity(record) for record in records]


@router.get('/{record_id}', response_model=VerificationResponse)
async def get_verification_endpoint(
    record_id: UUID,
    repository: RepositoryDep,
) -> VerificationResponse:
    """Return a single stored verification by id."""
    record = await repository.get(record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not_found')
    return VerificationResponse.from_entity(record)


@router.delete('/{record_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_verification_endpoint(
    record_id: UUID,
    repository: RepositoryDep,
) -> Response:
    """Delete a stored verification by id."""
    deleted = await repository.delete(record_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not_found')
    return Response(status_code=status.HTTP_204_NO_CONTENT)
