# PleaseTextMe: Auth Service

This is the Authentication Microservice for the PleaseTextMe project. It uses FastAPI, SQLAlchemy, PostgreSQL, and Redis.

## Getting Started with Docker

The entire project is dockerized and can be launched with a single click using Docker Compose. A `Makefile` is provided for convenience.

### Prerequisites
- Docker and Docker Compose installed on your system.
- Make (optional, but recommended).

### Environment Setup
Make sure you have a `.env` file in the root of this directory. It should contain at least:
```env
POSTGRES_PASSWORD=secret
SALT=U_AXELA_HUY_666_SM
# (Add any other necessary secrets for your JWT config here if needed later)
```

### Running the Project

You can start the entire infrastructure (Auth App, Postgres Database, and Redis) using the Makefile:

```bash
make up
```

Wait a few moments for the database to initialize and the application to run its migrations. The API will be available at:
`http://localhost:8000/api/openapi`

### Useful Makefile Commands

- `make up` - Start all containers in the background.
- `make down` - Stop and remove all containers.
- `make logs` - View logs for all containers in real-time.
- `make shell` - Open a terminal session inside the running Auth app container.
- `make migrate` - Run Alembic migrations manually.
- `make generate m="migration_name"` - Generate a new Alembic migration script.
- `make db-shell` - Connect directly to the PostgreSQL database.
- `make redis-shell` - Connect directly to the Redis store.

## Architecture

The project follows Clean/DDD Architecture using:
- **FastAPI** for routing and HTTP layer.
- **Dishka** for Dependency Injection.
- **SQLAlchemy** with imperative mapping.
- **Alembic** for migrations.
