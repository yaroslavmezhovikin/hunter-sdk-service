"""FastAPI application factory."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from hunter_sdk.api.routers.verifications import router as verifications_router
from hunter_sdk.sdk.client import HunterClient
from hunter_sdk.settings import (
    DatabaseSettings,
    HunterSettings,
    get_database_settings,
    get_hunter_settings,
)
from hunter_sdk.storage.database import build_engine, build_session_factory


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    hunter_settings: HunterSettings = app.state.hunter_settings
    database_settings: DatabaseSettings = app.state.database_settings

    sdk = HunterClient(
        api_key=hunter_settings.api_key,
        base_url=hunter_settings.base_url,
        timeout=hunter_settings.timeout,
    )
    engine = build_engine(database_settings.database_url, echo=database_settings.echo)
    session_factory = build_session_factory(engine)

    app.state.hunter_client = sdk
    app.state.engine = engine
    app.state.session_factory = session_factory

    try:
        yield
    finally:
        await sdk.aclose()
        await engine.dispose()


def create_app(
    hunter_settings: HunterSettings | None = None,
    database_settings: DatabaseSettings | None = None,
) -> FastAPI:
    """Build the FastAPI application instance."""
    app = FastAPI(
        title='Hunter.io SDK service',
        version='0.1.0',
        lifespan=_lifespan,
    )
    app.state.hunter_settings = hunter_settings or get_hunter_settings()
    app.state.database_settings = database_settings or get_database_settings()
    app.include_router(verifications_router)
    return app
