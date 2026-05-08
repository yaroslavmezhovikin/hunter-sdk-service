"""Run ``python -m hunter_sdk`` to start the FastAPI service via uvicorn."""

import uvicorn

from hunter_sdk.settings import get_app_settings


def main() -> None:
    """Entry point used by ``python -m hunter_sdk``."""
    app_settings = get_app_settings()
    uvicorn.run(
        'hunter_sdk.api.app:create_app',
        factory=True,
        host=app_settings.host,
        port=app_settings.port,
        log_level=app_settings.log_level.lower(),
    )


if __name__ == '__main__':
    main()
