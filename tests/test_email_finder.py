"""Tests for the ``EmailFinder`` endpoint."""

from typing import Final

import httpx
import respx

from hunter_sdk.sdk.endpoints.email_finder import EmailFinder
from hunter_sdk.sdk.transport import HunterTransport

_HTTP_OK: Final[int] = 200
_FINDER_SCORE: Final[int] = 97


async def test_find_email_sends_required_params(
    transport: HunterTransport,
    respx_mock: respx.MockRouter,
) -> None:
    """The endpoint sends ``domain``, ``first_name`` and ``last_name`` as query params."""
    route = respx_mock.get('/v2/email-finder').mock(
        return_value=httpx.Response(
            _HTTP_OK,
            json={
                'data': {
                    'email': 'patrick@stripe.com',
                    'first_name': 'Patrick',
                    'last_name': 'Collison',
                    'score': _FINDER_SCORE,
                },
            },
        ),
    )
    finder = EmailFinder(transport)
    finding = await finder(domain='stripe.com', first_name='Patrick', last_name='Collison')
    assert finding.email == 'patrick@stripe.com'
    last_request = route.calls.last.request
    sent_params = last_request.url.params
    assert sent_params['domain'] == 'stripe.com'
    assert sent_params['first_name'] == 'Patrick'
    assert sent_params['last_name'] == 'Collison'
