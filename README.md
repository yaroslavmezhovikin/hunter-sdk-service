# hunter-sdk

Async SDK + FastAPI service for [Hunter.io](https://hunter.io/api-documentation/v2),
backed by PostgreSQL via SQLAlchemy 2.0 (async) with an in-memory implementation
provided for tests and quick demos.

## Layout

```
src/hunter_sdk/
    sdk/            # Hunter.io HTTP client (httpx, async)
    storage/        # SQLAlchemy ORM + Postgres + in-memory repositories
    services/       # Service layer wiring SDK + storage
    api/            # FastAPI app, routers, schemas, DI providers
    settings.py     # pydantic-settings configuration
alembic/            # async migrations
tests/              # pytest + respx + ASGI lifespan tests
```

The repository follows the dependency-inversion principle: the `VerificationService`
depends on a `VerificationRepository` `Protocol`, which has two implementations:

- `PostgresVerificationRepository` (production, async SQLAlchemy)
- `InMemoryVerificationRepository` (sandbox/tests — matches the original
  "in-memory dictionary" specification)

## Endpoints

The Hunter.io SDK covers three endpoints:

| Method | Path                       | Purpose                                                 |
|--------|----------------------------|---------------------------------------------------------|
| GET    | `/v2/email-verifier`       | Verify a single email address                           |
| GET    | `/v2/email-finder`         | Find a likely email by name + domain                    |
| GET    | `/v2/domain-search`        | List public emails attributed to a domain               |

The FastAPI layer exposes them as JSON CRUD endpoints:

| Method | Path                            | Purpose                              |
|--------|---------------------------------|--------------------------------------|
| POST   | `/verifications/email`          | Verify and store an email            |
| POST   | `/verifications/find`           | Find an email and store the result   |
| POST   | `/verifications/domain`         | Search a domain and store the result |
| GET    | `/verifications`                | List stored verifications            |
| GET    | `/verifications/{record_id}`    | Read a single stored verification    |
| DELETE | `/verifications/{record_id}`    | Delete a stored verification         |

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
# Swagger UI: http://localhost:8000/docs
```

## Tests

```bash
pytest
```

Tests do not require PostgreSQL: the API tests override the repository
dependency with the in-memory implementation and `respx` mocks the
Hunter.io HTTP layer.

## Quality gates

```bash
mypy src
flake8 src tests
```

The `setup.cfg` is the one provided in the brief, with two minimal
adaptations for a FastAPI (non-Django) project:

- `[mypy] plugins` lists only `pydantic.mypy` (the `mypy_django_plugin`
  reference would import-fail without Django installed).
- The `[mypy.plugins.django-stubs]` and `[mypy-*.migrations.*]` Django
  sections are removed; `[mypy-alembic.*]` ignores Alembic migrations
  instead.

All other `flake8` / `pycodestyle` / `isort` rules are kept verbatim from
the gist.
