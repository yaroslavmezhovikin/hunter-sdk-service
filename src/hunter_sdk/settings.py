"""Application settings loaded from environment variables."""

from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_TIMEOUT_SECONDS: Final[float] = 10.0
_DEFAULT_PORT: Final[int] = 8000
_MAX_PORT_EXCLUSIVE: Final[int] = 65536


class HunterSettings(BaseSettings):
    """Configuration for the Hunter.io API client."""

    model_config = SettingsConfigDict(env_prefix='HUNTER_', env_file='.env', extra='ignore')

    api_key: str = Field(..., min_length=1)
    base_url: str = 'https://api.hunter.io'
    timeout: float = Field(default=_DEFAULT_TIMEOUT_SECONDS, gt=0)


class DatabaseSettings(BaseSettings):
    """Configuration for the PostgreSQL connection."""

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    database_url: str = Field(
        default='postgresql+asyncpg://hunter:hunter@localhost:5432/hunter',
    )
    echo: bool = False


class AppSettings(BaseSettings):
    """Configuration for the FastAPI application."""

    model_config = SettingsConfigDict(env_prefix='APP_', env_file='.env', extra='ignore')

    host: str = '127.0.0.1'
    port: int = Field(default=_DEFAULT_PORT, gt=0, lt=_MAX_PORT_EXCLUSIVE)
    log_level: str = 'INFO'


def get_hunter_settings() -> HunterSettings:
    """Return Hunter SDK settings."""
    return HunterSettings()


def get_database_settings() -> DatabaseSettings:
    """Return database settings."""
    return DatabaseSettings()


def get_app_settings() -> AppSettings:
    """Return FastAPI application settings."""
    return AppSettings()
