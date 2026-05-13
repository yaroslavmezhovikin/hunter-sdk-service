"""Tests for the ``EmailVerifier`` endpoint."""

from typing import Final

import httpx
import respx

from hunter_sdk.sdk.endpoints.email_verifier import EmailVerifier
from hunter_sdk.sdk.transport import HunterTransport

_HTTP_OK: Final[int] = 200
_VALID_SCORE: Final[int] = 91


async def test_verify_email_returns_parsed_response(
    transport: HunterTransport,
    respx_mock: respx.MockRouter,
) -> None:
    """The endpoint parses the API ``data`` envelope into ``EmailVerification``."""
    respx_mock.get('/v2/email-verifier').mock(
        return_value=httpx.Response(
            _HTTP_OK,
            json={
                'data': {
                    'email': 'patrick@stripe.com',
                    'status': 'valid',
                    'score': _VALID_SCORE,
                },
            },
        ),
    )
    verifier = EmailVerifier(transport)
    verification = await verifier(email='patrick@stripe.com')
    assert verification.email == 'patrick@stripe.com'
    assert verification.status == 'valid'
    assert verification.score == _VALID_SCORE
