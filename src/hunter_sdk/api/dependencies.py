"""FastAPI dependency providers wiring SDK, storage and service together."""

from typing import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from hunter_sdk.sdk.client import HunterClient
from hunter_sdk.services.verification import VerificationService
from hunter_sdk.storage.repositories.postgres import PostgresVerificationRepository


def get_hunter_client(request: Request) -> HunterClient:
    """Return the long-lived ``HunterClient`` stored on the FastAPI app state."""
    sdk: HunterClient = request.app.state.hunter_client
    return sdk


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    """Return the session factory stored on the FastAPI app state."""
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    return factory


async def get_session(
    factory: async_sessionmaker[AsyncSession] = Depends(get_session_factory),
) -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped async session."""
    async with factory() as session:
        yield session


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresVerificationRepository:
    """Build a request-scoped Postgres repository."""
    return PostgresVerificationRepository(session)


def get_verification_service(
    sdk: HunterClient = Depends(get_hunter_client),
    repository: PostgresVerificationRepository = Depends(get_repository),
) -> VerificationService:
    """Build a request-scoped verification service."""
    return VerificationService(sdk=sdk, repository=repository)
