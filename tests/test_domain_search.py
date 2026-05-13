"""Tests for the ``DomainSearch`` endpoint."""

from typing import Final

import httpx
import respx

from hunter_sdk.sdk.endpoints.domain_search import DomainSearch
from hunter_sdk.sdk.transport import HunterTransport

_HTTP_OK: Final[int] = 200
_CONFIDENCE: Final[int] = 95
_EXPECTED_EMAIL_COUNT: Final[int] = 1


async def test_search_domain_returns_emails(
    transport: HunterTransport,
    respx_mock: respx.MockRouter,
) -> None:
    """The endpoint parses ``data.emails`` into ``DomainEmail`` objects."""
    respx_mock.get('/v2/domain-search').mock(
        return_value=httpx.Response(
            _HTTP_OK,
            json={
                'data': {
                    'domain': 'stripe.com',
                    'organization': 'Stripe',
                    'emails': [
                        {
                            'value': 'patrick@stripe.com',
                            'type': 'personal',
                            'confidence': _CONFIDENCE,
                        },
                    ],
                },
            },
        ),
    )
    domain_search = DomainSearch(transport)
    search_result = await domain_search(domain='stripe.com')
    assert search_result.domain == 'stripe.com'
    assert search_result.organization == 'Stripe'
    assert len(search_result.emails) == _EXPECTED_EMAIL_COUNT
    assert search_result.emails[0].email_address == 'patrick@stripe.com'
