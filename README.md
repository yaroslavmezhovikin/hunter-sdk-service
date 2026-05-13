# hunter-sdk-service

Async SDK + FastAPI service for [Hunter.io](https://hunter.io/api-documentation/v2),
backed by PostgreSQL via SQLAlchemy 2.0 (async), with an in-memory
implementation provided for tests and quick demos.

## Layout

```
src/hunter_sdk/
    sdk/
        transport.py         # HunterTransport — HTTP + auth + error translation
        endpoints/
            email_verifier.py
            email_finder.py
            domain_search.py
        models.py
        exceptions.py
    storage/
        database.py
        orm.py
        entities.py
        repositories/
            base.py          # VerificationRepository Protocol
            postgres.py      # async SQLAlchemy implementation
            memory.py        # in-memory dict implementation
    services/
        verification.py      # orchestrates endpoints + persistence
    api/
        app.py
        dependencies.py      # Annotated-based DI providers
        routers/verifications.py
        schemas.py
    migrations/              # alembic, async migrations
        env.py
        versions/0001_initial.py
    settings.py
tests/
    test_transport.py
    test_email_verifier.py
    test_email_finder.py
    test_domain_search.py
    test_memory_repository.py
    test_verification_service.py
    test_api.py
```

## Design notes

**SDK is additive, not mutative.** The SDK is split into a tiny
transport and one file per endpoint. Adding a new Hunter.io endpoint
(e.g. `discover`) is a single new file — `sdk/endpoints/discover.py` —
defining a small class with `__init__(transport)` and `__call__(...)`.
No existing file is modified. The transport stays the same regardless
of how many endpoints exist.

**Dependency-inversion at the storage boundary.** The service depends on
the `VerificationRepository` `Protocol`, not on SQLAlchemy. Two
implementations ship: `PostgresVerificationRepository` (async
SQLAlchemy + asyncpg) for production and `InMemoryVerificationRepository`
(matches the original "in-memory dictionary" brief) for tests.

**The service is an orchestrator, not a pass-through.** It only owns
operations that combine an SDK call with persistence
(`verify_email`, `find_email`, `search_domain`). Pure storage queries
(list / get by id / delete) go straight through the repository — the
service does not wrap them.

**FastAPI dependency injection uses the `Annotated[T, Depends(...)]`
form throughout.** This avoids `Depends(...)` as a function default,
which would trigger both `B008` (function call as default) and
`WPS404` (complex default value).

## Endpoints

Hunter.io endpoints exposed by the SDK:

| Method | Path                       | Purpose                                                 |
|--------|----------------------------|---------------------------------------------------------|
| GET    | `/v2/email-verifier`       | Verify a single email address                           |
| GET    | `/v2/email-finder`         | Find a likely email by name + domain                    |
| GET    | `/v2/domain-search`        | List public emails attributed to a domain               |

FastAPI surface:

| Method | Path                            | Goes through                  |
|--------|---------------------------------|-------------------------------|
| POST   | `/verifications/email`          | service → SDK → repository    |
| POST   | `/verifications/find`           | service → SDK → repository    |
| POST   | `/verifications/domain`         | service → SDK → repository    |
| GET    | `/verifications`                | repository (direct)           |
| GET    | `/verifications/{record_id}`    | repository (direct)           |
| DELETE | `/verifications/{record_id}`    | repository (direct)           |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate         # PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env              # then edit HUNTER_API_KEY
```

Start PostgreSQL and apply migrations:

```bash
docker compose up -d postgres
alembic upgrade head
```

## Run

```bash
python -m hunter_sdk
# Swagger UI: http://127.0.0.1:8000/docs
```

The service binds to `127.0.0.1:8000` by default. Override via env vars
when running outside localhost, e.g. inside a container:

```bash
APP_HOST=0.0.0.0 APP_PORT=8080 python -m hunter_sdk
```

## Tests

```bash
pytest
```

Tests do not require PostgreSQL — `test_api.py` overrides the repository
dependency with the in-memory implementation, and `respx` mocks the
Hunter.io HTTP layer.

## Quality gates

```bash
mypy src tests
flake8 src tests
```

`setup.cfg` is the gist from the brief, kept verbatim. The only
adaptations are FastAPI-specific (not relaxations of the rules):

- `[mypy] plugins` lists `pydantic.mypy` instead of
  `mypy_django_plugin.main` — the Django plugin would import-fail in a
  non-Django project. Pydantic is used heavily, so its mypy plugin is
  kept.
- The `[mypy.plugins.django-stubs]` section is removed for the same
  reason.
- Migrations live under `src/hunter_sdk/migrations/`, so they are
  already covered by the gist's existing `*/migrations/*` flake8 exclude
  and the `[mypy-*.migrations.*]` ignore section (same convention as
  Django apps).
- `[flake8] per-file-ignores` disables exactly one rule for tests only:
  `S101` (bandit "use of assert"), which is fundamentally incompatible
  with the pytest idiom. Production code under `src/` remains under the
  full strict ruleset.

Linter state:

- `mypy src tests` — 0 errors across 38 source files.
- `flake8 src tests` — 0 violations under the gist's ignore list.
- `pytest` — 15 tests passing.
