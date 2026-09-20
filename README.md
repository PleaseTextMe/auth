# PleaseTextMe: Auth Service

This is the Authentication Microservice for the PleaseTextMe project. It uses FastAPI, SQLAlchemy, PostgreSQL, and Redis.

## Getting Started with Docker

The entire project is dockerized and can be launched with a single click using Docker Compose. A `Makefile` is provided for convenience.

### Prerequisites
- Docker and Docker Compose installed on your system.
- Make (optional, but recommended).

### Environment Setup
Make sure you have a `.env` file in the root of this directory (copy from `.env.example` if needed):
```env
POSTGRES_PASSWORD=secret
```

For test environments, copy `.env.test.example` to `.env.test`:
```bash
cp .env.test.example .env.test
```

---

## Running the Application

You can start the entire infrastructure (Auth App, Postgres Database, and Redis) using the Makefile:

```bash
make up
```

Wait a few moments for the database to initialize and the application to run its migrations.

### Useful Endpoints
- **OpenAPI Docs**: `http://localhost:8000/api/openapi`
- **Health Check**: `http://localhost:8000/api/health`

---

## Running Tests

### 1. Local Testing via Pytest
Install development dependencies and run tests:
```bash
pip install -r requirements-dev.txt
pytest
```

### 2. Isolated Docker Test Environment
To spin up a separate Postgres & Redis container setup dedicated for running tests:
```bash
docker compose -f tests/docker-compose.test.yml up -d
pytest
docker compose -f tests/docker-compose.test.yml down
```

---

## CI/CD & Automated Checks

This microservice uses **GitHub Actions** (`.github/workflows/ci.yml`) to enforce code quality on every push and Pull Request:
1. **Linter & Formatting check**: `flake8` / `ruff`
2. **Automated Unit & Integration Tests**: `pytest`

---

## Useful Makefile Commands

- `make up` - Start all containers in the background.
- `make down` - Stop and remove all containers.
- `make logs` - View logs for all containers in real-time.
- `make shell` - Open a terminal session inside the running Auth app container.
- `make migrate` - Run Alembic migrations manually.
- `make generate m="migration_name"` - Generate a new Alembic migration script.
- `make db-shell` - Connect directly to the PostgreSQL database.
- `make redis-shell` - Connect directly to the Redis store.

---

## Architecture

The project follows Clean/DDD Architecture using:
- **FastAPI** for routing and HTTP layer.
- **Dishka** for Dependency Injection.
- **SQLAlchemy** with imperative mapping.
- **Alembic** for migrations.
