"""FastAPI dependency providers wiring transport, repository and service together.

All providers use the ``Annotated`` injection form so callers never have a
``Depends(...)`` expression as a default value — that pattern triggers
both ``B008`` (function call as default) and ``WPS404`` (complex default).
"""

from typing import Annotated, AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from hunter_sdk.sdk.transport import HunterTransport
from hunter_sdk.services.verification import VerificationService
from hunter_sdk.storage.repositories.base import VerificationRepository
from hunter_sdk.storage.repositories.postgres import PostgresVerificationRepository


def get_transport(request: Request) -> HunterTransport:
    """Return the transport stored on the FastAPI app state."""
    transport: HunterTransport = request.app.state.transport
    return transport


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    """Return the session factory stored on the FastAPI app state."""
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    return factory


SessionFactoryDep = Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)]


async def open_session(factory: SessionFactoryDep) -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped async session."""
    async with factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(open_session)]


def get_repository(session: SessionDep) -> VerificationRepository:
    """Build a request-scoped repository instance."""
    return PostgresVerificationRepository(session)


TransportDep = Annotated[HunterTransport, Depends(get_transport)]
RepositoryDep = Annotated[VerificationRepository, Depends(get_repository)]


def get_verification_service(
    transport: TransportDep,
    repository: RepositoryDep,
) -> VerificationService:
    """Build a request-scoped verification service."""
    return VerificationService(transport=transport, repository=repository)


ServiceDep = Annotated[VerificationService, Depends(get_verification_service)]
