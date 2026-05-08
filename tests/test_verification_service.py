"""Tests covering the service layer end-to-end with an in-memory repository."""

import httpx
import respx

from hunter_sdk.sdk.client import HunterClient
from hunter_sdk.services.verification import (
    OPERATION_DOMAIN_SEARCH,
    OPERATION_VERIFY_EMAIL,
    VerificationService,
)
from hunter_sdk.storage.repositories.memory import InMemoryVerificationRepository


async def test_verify_email_persists_record(
    hunter_client: HunterClient,
    memory_repository: InMemoryVerificationRepository,
    respx_mock: respx.MockRouter,
) -> None:
    respx_mock.get('/v2/email-verifier').mock(
        return_value=httpx.Response(
            200,
            json={'data': {'email': 'a@b.com', 'status': 'valid', 'score': 80}},
        ),
    )
    service = VerificationService(sdk=hunter_client, repository=memory_repository)

    record = await service.verify_email('a@b.com')

    assert record.operation == OPERATION_VERIFY_EMAIL
    assert record.query == {'email': 'a@b.com'}
    assert record.response['status'] == 'valid'
    assert record.response['score'] == 80
    listed = await memory_repository.list_all()
    assert len(listed) == 1


async def test_search_domain_persists_record(
    hunter_client: HunterClient,
    memory_repository: InMemoryVerificationRepository,
    respx_mock: respx.MockRouter,
) -> None:
    respx_mock.get('/v2/domain-search').mock(
        return_value=httpx.Response(
            200,
            json={
                'data': {
                    'domain': 'stripe.com',
                    'organization': 'Stripe',
                    'emails': [],
                },
            },
        ),
    )
    service = VerificationService(sdk=hunter_client, repository=memory_repository)

    record = await service.search_domain('stripe.com')

    assert record.operation == OPERATION_DOMAIN_SEARCH
    assert record.response['domain'] == 'stripe.com'
