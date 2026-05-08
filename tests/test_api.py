"""Integration tests for the FastAPI surface using an in-memory repository."""

from typing import AsyncIterator, Final

import httpx
import pytest_asyncio
import respx
from asgi_lifespan import LifespanManager

from hunter_sdk.api.app import create_app
from hunter_sdk.api.dependencies import get_repository
from hunter_sdk.settings import DatabaseSettings, HunterSettings
from hunter_sdk.storage.repositories.memory import InMemoryVerificationRepository

_BASE_URL: Final[str] = 'https://api.hunter.io'
_HTTP_CREATED: Final[int] = 201
_HTTP_OK: Final[int] = 200
_HTTP_NO_CONTENT: Final[int] = 204
_HTTP_NOT_FOUND: Final[int] = 404


@pytest_asyncio.fixture
async def api_client() -> AsyncIterator[tuple[httpx.AsyncClient, InMemoryVerificationRepository]]:
    hunter_settings = HunterSettings(
        api_key='test',
        base_url=_BASE_URL,
        timeout=5.0,
    )
    database_settings = DatabaseSettings(
        database_url='postgresql+asyncpg://test:test@localhost:5432/test',
    )
    app = create_app(hunter_settings=hunter_settings, database_settings=database_settings)

    repository = InMemoryVerificationRepository()
    app.dependency_overrides[get_repository] = lambda: repository

    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url='http://testserver',
        ) as client:
            yield client, repository


async def test_post_email_creates_record(
    api_client: tuple[httpx.AsyncClient, InMemoryVerificationRepository],
) -> None:
    client, repository = api_client
    with respx.mock(base_url=_BASE_URL, assert_all_called=False) as mock_router:
        mock_router.get('/v2/email-verifier').mock(
            return_value=httpx.Response(
                200,
                json={'data': {'email': 'a@b.com', 'status': 'valid', 'score': 70}},
            ),
        )

        response = await client.post('/verifications/email', json={'email': 'a@b.com'})

    assert response.status_code == _HTTP_CREATED
    body = response.json()
    assert body['operation'] == 'verify_email'
    assert body['response']['status'] == 'valid'
    assert len(await repository.list_all()) == 1


async def test_get_missing_record_returns_404(
    api_client: tuple[httpx.AsyncClient, InMemoryVerificationRepository],
) -> None:
    client, _ = api_client
    response = await client.get('/verifications/00000000-0000-0000-0000-000000000000')
    assert response.status_code == _HTTP_NOT_FOUND


async def test_list_then_delete_round_trip(
    api_client: tuple[httpx.AsyncClient, InMemoryVerificationRepository],
) -> None:
    client, repository = api_client
    with respx.mock(base_url=_BASE_URL, assert_all_called=False) as mock_router:
        mock_router.get('/v2/domain-search').mock(
            return_value=httpx.Response(
                200,
                json={'data': {'domain': 'stripe.com', 'organization': 'Stripe', 'emails': []}},
            ),
        )
        created = await client.post('/verifications/domain', json={'domain': 'stripe.com'})

    assert created.status_code == _HTTP_CREATED
    record_id = created.json()['record_id']

    listed = await client.get('/verifications')
    assert listed.status_code == _HTTP_OK
    assert len(listed.json()) == 1

    deleted = await client.delete('/verifications/{0}'.format(record_id))
    assert deleted.status_code == _HTTP_NO_CONTENT
    assert await repository.list_all() == []
