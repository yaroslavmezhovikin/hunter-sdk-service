"""Integration tests for the FastAPI surface using an in-memory repository."""

from typing import AsyncIterator, Final

import httpx
import pytest_asyncio
import respx
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from hunter_sdk.api.app import create_app
from hunter_sdk.api.dependencies import get_repository
from hunter_sdk.settings import DatabaseSettings, HunterSettings
from hunter_sdk.storage.entities import NewVerification
from hunter_sdk.storage.repositories.memory import InMemoryVerificationRepository

_BASE_URL: Final[str] = 'https://api.hunter.io'
_HTTP_OK: Final[int] = 200
_HTTP_CREATED: Final[int] = 201
_HTTP_NO_CONTENT: Final[int] = 204
_HTTP_NOT_FOUND: Final[int] = 404
_TEST_TIMEOUT: Final[float] = 5.0
_TEST_SCORE: Final[int] = 70
_EXPECTED_RECORD_COUNT: Final[int] = 1


def _build_test_app() -> tuple[FastAPI, InMemoryVerificationRepository]:
    hunter_settings = HunterSettings(
        api_key='test',
        base_url=_BASE_URL,
        timeout=_TEST_TIMEOUT,
    )
    database_settings = DatabaseSettings(
        database_url='postgresql+asyncpg://test:test@localhost:5432/test',
    )
    app = create_app(hunter_settings=hunter_settings, database_settings=database_settings)
    repository = InMemoryVerificationRepository()
    app.dependency_overrides[get_repository] = lambda: repository
    return app, repository


@pytest_asyncio.fixture
async def api_client() -> AsyncIterator[tuple[httpx.AsyncClient, InMemoryVerificationRepository]]:
    """Yield an ASGI httpx client and the in-memory repository."""
    app, repository = _build_test_app()
    async with LifespanManager(app):
        asgi_transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=asgi_transport,
            base_url='http://testserver',
        ) as client:
            yield client, repository


async def test_post_email_creates_record(
    api_client: tuple[httpx.AsyncClient, InMemoryVerificationRepository],
) -> None:
    """``POST /verifications/email`` persists a record built from the SDK response."""
    client, repository = api_client
    with respx.mock(base_url=_BASE_URL, assert_all_called=False) as mock_router:
        mock_router.get('/v2/email-verifier').mock(
            return_value=httpx.Response(
                _HTTP_OK,
                json={'data': {'email': 'a@b.com', 'status': 'valid', 'score': _TEST_SCORE}},
            ),
        )
        response = await client.post('/verifications/email', json={'email': 'a@b.com'})

    assert response.status_code == _HTTP_CREATED
    body = response.json()
    assert body['operation'] == 'verify_email'
    assert body['response']['status'] == 'valid'
    assert len(await repository.list_all()) == _EXPECTED_RECORD_COUNT


async def test_get_missing_record_returns_not_found(
    api_client: tuple[httpx.AsyncClient, InMemoryVerificationRepository],
) -> None:
    """``GET /verifications/{id}`` returns 404 when the id is unknown."""
    client, _ = api_client
    response = await client.get('/verifications/00000000-0000-0000-0000-000000000000')
    assert response.status_code == _HTTP_NOT_FOUND


async def test_list_returns_persisted_records(
    api_client: tuple[httpx.AsyncClient, InMemoryVerificationRepository],
) -> None:
    """``GET /verifications`` returns every stored record."""
    client, repository = api_client
    await repository.create(
        NewVerification(operation='verify_email', query={}, response={'status': 'valid'}),
    )
    response = await client.get('/verifications')
    assert response.status_code == _HTTP_OK
    assert len(response.json()) == _EXPECTED_RECORD_COUNT


async def test_delete_removes_record(
    api_client: tuple[httpx.AsyncClient, InMemoryVerificationRepository],
) -> None:
    """``DELETE /verifications/{id}`` removes a previously stored record."""
    client, repository = api_client
    stored = await repository.create(
        NewVerification(operation='verify_email', query={}, response={}),
    )
    response = await client.delete('/verifications/{0}'.format(stored.record_id))
    assert response.status_code == _HTTP_NO_CONTENT
    assert await repository.list_all() == []
