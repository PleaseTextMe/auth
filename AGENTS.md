# AGENTS.md

## Stack

FastAPI + SQLAlchemy (async, asyncpg) + Alembic + Dishka (DI) + Pydantic/pydantic-settings + PostgreSQL. Python 3.12, venv at `.venv/`.

**No `pyproject.toml` or `requirements.txt` exists.** Dependencies are installed directly in `.venv` via pip. To see what's installed: `.venv/bin/pip list`.

## Running

```bash
PYTHONPATH=. .venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

`PYTHONPATH` must include the project root -- all imports use the `src.` prefix (e.g. `from src.core.config import settings`).

OpenAPI docs are at `/api/openapi` (non-default). API routes are prefixed `/api/v1/`.

## Environment

Config loaded via pydantic-settings from `.env`. Required vars: `POSTGRES_PASSWORD`, `SECRET`, `SECRET_KEY`, `JWT_ALGORITHM`. Postgres defaults to `localhost:5432/please_text_me_db` with user `postgres`.

## Architecture (non-obvious parts)

- **Dishka DI**, not standard FastAPI `Depends` for service injection. Services are provided via `Container` in `src/infrastructure/container.py` and injected with `FromDishka[IService]` + `DishkaRoute` on routers.
- **Imperative SQLAlchemy mapping**: Domain entities are plain Pydantic models (`src/domain/entities/`). SQL tables are defined separately (`src/infrastructure/models/`). Mapping happens at startup via `mapper_registry.map_imperatively()` called from `start_mappers()` in `src/infrastructure/models/__init__.py`.
- **Snowflake IDs** (not UUIDs) via the `snowflake-id` package for primary keys.
- **Unit of Work pattern**: Services receive `IUnitOfWork`, use it as async context manager. Repositories are accessed as properties on UoW (e.g. `uow.user_repository`).

### Layer responsibilities

| Layer | Path | Role |
|---|---|---|
| API | `src/api/v1/` | FastAPI routers, schemas, dependency helpers |
| Domain | `src/domain/` | Pydantic entities and DTOs (no DB dependency) |
| Services | `src/services/` | Business logic + ABC interfaces |
| Infrastructure | `src/infrastructure/` | SQLAlchemy models, repositories, UoW, DI container, DB lifecycle |
| Interfaces | `src/interfaces/` | Abstract lifetime protocol |
| Core | `src/core/` | Config, logging, utilities (snowflake, datetime) |

## Migrations (Alembic)

```bash
PYTHONPATH=. .venv/bin/alembic upgrade head
PYTHONPATH=. .venv/bin/alembic revision --autogenerate -m "description"
```

Alembic config: `alembic.ini`, scripts at `src/infrastructure/db/migrations/`. The migration env.py uses **psycopg2 (sync)** driver (`connection_url_2`), while the app uses **asyncpg**. Both are configured in `src/core/config.py` on `PostgresSettings`.

## Tests

pytest is configured (`.vscode/settings.json`) but the `tests/` directory is empty. No conftest, no test config files.

## WIP / known broken code

The codebase is under active development. Several endpoints in `src/api/v1/endpoints/auth.py` (register, login, logout, refresh) reference undefined names (`AuthDep`, `JWTDep`, `SessionDep`, `SessionFactory`, `BlacklistDep`, `PasswordsNotMatch`, `SessionHasExpired`, `Forbidden`, `get_refresh_token`, `set_refresh_token`). Only the `GET /salt` endpoint appears functional.

Many features are commented out throughout (RabbitMQ producer, Redis, additional repositories/entities).
