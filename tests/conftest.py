"""Shared pytest fixtures."""

from typing import AsyncIterator, Final, Iterator

import httpx
import pytest
import pytest_asyncio
import respx

from hunter_sdk.sdk.transport import HunterTransport
from hunter_sdk.storage.repositories.memory import InMemoryVerificationRepository

API_KEY: Final[str] = 'test-api-key'
BASE_URL: Final[str] = 'https://api.hunter.io'

_TIMEOUT_SECONDS: Final[float] = 5.0


@pytest.fixture
def respx_mock() -> Iterator[respx.MockRouter]:
    """Provide a respx router scoped to the Hunter base URL."""
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as mock_router:
        yield mock_router


@pytest_asyncio.fixture
async def transport() -> AsyncIterator[HunterTransport]:
    """Yield a transport backed by a real httpx async client."""
    async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as http_client:
        yield HunterTransport(api_key=API_KEY, base_url=BASE_URL, http_client=http_client)


@pytest.fixture
def memory_repository() -> InMemoryVerificationRepository:
    """Provide a fresh in-memory repository per test."""
    return InMemoryVerificationRepository()
