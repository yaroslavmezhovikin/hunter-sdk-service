"""Tests for the Hunter.io transport (auth, error translation, lifecycle)."""

from typing import Final

import httpx
import pytest
import respx

from hunter_sdk.sdk.exceptions import HunterAPIError, HunterTimeoutError
from hunter_sdk.sdk.transport import HunterTransport

_HTTP_UNAUTHORIZED: Final[int] = 401


async def test_api_error_translation(
    transport: HunterTransport,
    respx_mock: respx.MockRouter,
) -> None:
    """Non-2xx responses raise ``HunterAPIError`` with the status preserved."""
    respx_mock.get('/v2/email-verifier').mock(
        return_value=httpx.Response(_HTTP_UNAUTHORIZED, text='unauthorized'),
    )
    with pytest.raises(HunterAPIError) as exc_info:
        await transport.get('/v2/email-verifier', {'email': 'a@b.com'})
    assert exc_info.value.status_code == _HTTP_UNAUTHORIZED


async def test_timeout_translation(
    transport: HunterTransport,
    respx_mock: respx.MockRouter,
) -> None:
    """``httpx.TimeoutException`` is wrapped in ``HunterTimeoutError``."""
    respx_mock.get('/v2/email-verifier').mock(side_effect=httpx.TimeoutException('boom'))
    with pytest.raises(HunterTimeoutError):
        await transport.get('/v2/email-verifier', {'email': 'a@b.com'})
