"""Tests for the Hunter.io SDK client."""

import httpx
import pytest
import respx

from hunter_sdk.sdk.client import HunterClient
from hunter_sdk.sdk.exceptions import HunterAPIError, HunterTimeoutError


async def test_verify_email_returns_parsed_response(
    hunter_client: HunterClient,
    respx_mock: respx.MockRouter,
) -> None:
    respx_mock.get('/v2/email-verifier').mock(
        return_value=httpx.Response(
            200,
            json={
                'data': {
                    'email': 'patrick@stripe.com',
                    'status': 'valid',
                    'score': 91,
                },
            },
        ),
    )

    verification = await hunter_client.verify_email('patrick@stripe.com')

    assert verification.email == 'patrick@stripe.com'
    assert verification.status == 'valid'
    assert verification.score == 91


async def test_find_email_sends_required_params(
    hunter_client: HunterClient,
    respx_mock: respx.MockRouter,
) -> None:
    route = respx_mock.get('/v2/email-finder').mock(
        return_value=httpx.Response(
            200,
            json={
                'data': {
                    'email': 'patrick@stripe.com',
                    'first_name': 'Patrick',
                    'last_name': 'Collison',
                    'score': 97,
                },
            },
        ),
    )

    finding = await hunter_client.find_email('stripe.com', 'Patrick', 'Collison')

    assert finding.email == 'patrick@stripe.com'
    sent_params = route.calls.last.request.url.params
    assert sent_params['domain'] == 'stripe.com'
    assert sent_params['first_name'] == 'Patrick'
    assert sent_params['last_name'] == 'Collison'


async def test_search_domain_returns_emails(
    hunter_client: HunterClient,
    respx_mock: respx.MockRouter,
) -> None:
    respx_mock.get('/v2/domain-search').mock(
        return_value=httpx.Response(
            200,
            json={
                'data': {
                    'domain': 'stripe.com',
                    'organization': 'Stripe',
                    'emails': [
                        {'value': 'patrick@stripe.com', 'type': 'personal', 'confidence': 95},
                    ],
                },
            },
        ),
    )

    search = await hunter_client.search_domain('stripe.com')

    assert search.domain == 'stripe.com'
    assert search.organization == 'Stripe'
    assert len(search.emails) == 1
    assert search.emails[0].email_address == 'patrick@stripe.com'


async def test_api_error_raises(
    hunter_client: HunterClient,
    respx_mock: respx.MockRouter,
) -> None:
    respx_mock.get('/v2/email-verifier').mock(
        return_value=httpx.Response(401, text='unauthorized'),
    )

    with pytest.raises(HunterAPIError) as exc_info:
        await hunter_client.verify_email('a@b.com')

    assert exc_info.value.status_code == 401


async def test_timeout_raises(
    hunter_client: HunterClient,
    respx_mock: respx.MockRouter,
) -> None:
    respx_mock.get('/v2/email-verifier').mock(side_effect=httpx.TimeoutException('boom'))

    with pytest.raises(HunterTimeoutError):
        await hunter_client.verify_email('a@b.com')
