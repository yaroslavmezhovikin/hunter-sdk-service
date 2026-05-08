"""Tests for the in-memory verification repository."""

from uuid import uuid4

from hunter_sdk.storage.entities import NewVerification
from hunter_sdk.storage.repositories.memory import InMemoryVerificationRepository


async def test_create_then_get_round_trip(
    memory_repository: InMemoryVerificationRepository,
) -> None:
    stored = await memory_repository.create(
        NewVerification(
            operation='verify_email',
            query={'email': 'a@b.com'},
            response={'status': 'valid'},
        ),
    )

    fetched = await memory_repository.get(stored.record_id)

    assert fetched is not None
    assert fetched.record_id == stored.record_id
    assert fetched.operation == 'verify_email'


async def test_list_orders_newest_first(
    memory_repository: InMemoryVerificationRepository,
) -> None:
    first = await memory_repository.create(
        NewVerification(operation='verify_email', query={}, response={}),
    )
    second = await memory_repository.create(
        NewVerification(operation='verify_email', query={}, response={}),
    )

    listed = await memory_repository.list_all()

    assert [record.record_id for record in listed] == [second.record_id, first.record_id]


async def test_update_replaces_response(
    memory_repository: InMemoryVerificationRepository,
) -> None:
    stored = await memory_repository.create(
        NewVerification(operation='verify_email', query={}, response={'old': True}),
    )

    updated = await memory_repository.update(
        stored.record_id,
        response={'fresh': True},
    )

    assert updated is not None
    assert updated.response == {'fresh': True}


async def test_delete_returns_true_when_present(
    memory_repository: InMemoryVerificationRepository,
) -> None:
    stored = await memory_repository.create(
        NewVerification(operation='verify_email', query={}, response={}),
    )

    deleted_existing = await memory_repository.delete(stored.record_id)
    deleted_missing = await memory_repository.delete(uuid4())

    assert deleted_existing is True
    assert deleted_missing is False
    assert await memory_repository.get(stored.record_id) is None
