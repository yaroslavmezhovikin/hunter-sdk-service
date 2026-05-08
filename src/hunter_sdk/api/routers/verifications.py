"""HTTP endpoints exposing the verification service."""

from typing import Final
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from hunter_sdk.api.dependencies import get_verification_service
from hunter_sdk.api.schemas import (
    DomainSearchRequest,
    FindEmailRequest,
    VerificationResponse,
    VerifyEmailRequest,
)
from hunter_sdk.sdk.exceptions import HunterAPIError, HunterTimeoutError
from hunter_sdk.services.verification import VerificationService

router = APIRouter(prefix='/verifications', tags=['verifications'])

_MAX_PAGE_SIZE: Final[int] = 200
_DEFAULT_PAGE_SIZE: Final[int] = 50


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
    service: VerificationService = Depends(get_verification_service),
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
    service: VerificationService = Depends(get_verification_service),
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
    service: VerificationService = Depends(get_verification_service),
) -> VerificationResponse:
    """Search public emails for a domain and persist the result."""
    try:
        record = await service.search_domain(body.domain)
    except (HunterAPIError, HunterTimeoutError) as sdk_exc:
        raise _translate_sdk_errors(sdk_exc) from sdk_exc
    return VerificationResponse.from_entity(record)


@router.get('', response_model=list[VerificationResponse])
async def list_verifications_endpoint(
    limit: int = Query(default=_DEFAULT_PAGE_SIZE, gt=0, le=_MAX_PAGE_SIZE),
    offset: int = Query(default=0, ge=0),
    service: VerificationService = Depends(get_verification_service),
) -> list[VerificationResponse]:
    """List stored verifications, newest first."""
    records = await service.list_all(limit=limit, offset=offset)
    return [VerificationResponse.from_entity(record) for record in records]


@router.get('/{record_id}', response_model=VerificationResponse)
async def get_verification_endpoint(
    record_id: UUID,
    service: VerificationService = Depends(get_verification_service),
) -> VerificationResponse:
    """Return a single stored verification by id."""
    record = await service.get(record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not_found')
    return VerificationResponse.from_entity(record)


@router.delete('/{record_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_verification_endpoint(
    record_id: UUID,
    service: VerificationService = Depends(get_verification_service),
) -> Response:
    """Delete a stored verification by id."""
    deleted = await service.delete(record_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not_found')
    return Response(status_code=status.HTTP_204_NO_CONTENT)
