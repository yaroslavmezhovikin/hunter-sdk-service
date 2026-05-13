"""Tests covering the service layer end-to-end with an in-memory repository."""

from typing import Final

import httpx
import respx

from hunter_sdk.sdk.transport import HunterTransport
from hunter_sdk.services.verification import OPERATION_DOMAIN_SEARCH, OPERATION_VERIFY_EMAIL, VerificationService
from hunter_sdk.storage.repositories.memory import InMemoryVerificationRepository

_HTTP_OK: Final[int] = 200
_TEST_SCORE: Final[int] = 80
_EXPECTED_RECORD_COUNT: Final[int] = 1


async def test_verify_email_persists_record(
    transport: HunterTransport,
    memory_repository: InMemoryVerificationRepository,
    respx_mock: respx.MockRouter,
) -> None:
    """``verify_email`` calls the SDK and stores the response."""
    respx_mock.get('/v2/email-verifier').mock(
        return_value=httpx.Response(
            _HTTP_OK,
            json={'data': {'email': 'a@b.com', 'status': 'valid', 'score': _TEST_SCORE}},
        ),
    )
    service = VerificationService(transport=transport, repository=memory_repository)
    record = await service.verify_email('a@b.com')
    assert record.operation == OPERATION_VERIFY_EMAIL
    assert record.query == {'email': 'a@b.com'}
    assert record.response['status'] == 'valid'
    assert record.response['score'] == _TEST_SCORE
    listed = await memory_repository.list_all()
    assert len(listed) == _EXPECTED_RECORD_COUNT


async def test_search_domain_persists_record(
    transport: HunterTransport,
    memory_repository: InMemoryVerificationRepository,
    respx_mock: respx.MockRouter,
) -> None:
    """``search_domain`` calls the SDK and stores the response."""
    respx_mock.get('/v2/domain-search').mock(
        return_value=httpx.Response(
            _HTTP_OK,
            json={
                'data': {
                    'domain': 'stripe.com',
                    'organization': 'Stripe',
                    'emails': [],
                },
            },
        ),
    )
    service = VerificationService(transport=transport, repository=memory_repository)
    record = await service.search_domain('stripe.com')
    assert record.operation == OPERATION_DOMAIN_SEARCH
    assert record.response['domain'] == 'stripe.com'
