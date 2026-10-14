import asyncio
import os
import subprocess
import sys
from typing import AsyncGenerator

import httpx
import pytest
import redis.asyncio as aioredis
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Select test settings before importing application modules that initialize them.
# Ruff 0.4.8 requires explicit E402 exceptions for this environment setup.
os.environ["ENV_FILE"] = ".env.test"

from src.core.config import settings  # noqa: E402
from src.infrastructure.db.postgres import get_session  # noqa: E402
from src.main import create_app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_docker_infrastructure(request):  # noqa: C901
    """Start docker-compose and run migrations for tests."""
    has_integration = any(item.get_closest_marker("integration") for item in request.session.items)
    if not has_integration:
        yield
        return

    compose_file = "tests/docker-compose.test.yml"
    compose_command = ["docker", "compose", "--env-file", ".env.test", "-f", compose_file]
    compose_started = False
    try:
        print("\nStarting test infrastructure...")
        try:
            subprocess.run(
                [*compose_command, "up", "-d"],
                check=True,
                capture_output=True,
                text=True,
            )
            compose_started = True
        except subprocess.CalledProcessError as e:
            print(
                f"\nWarning: Failed to auto-start docker infrastructure. Error:\n{e.stderr}\nMake sure to run 'sudo docker compose --env-file .env.test -f {compose_file} up -d' manually before running tests."
            )

        print("Waiting for Postgres to be ready...")

        async def check_db():
            engine = create_async_engine(settings.postgres.connection_url)
            try:
                for _ in range(10):
                    try:
                        async with engine.connect() as conn:
                            await conn.execute(text("SELECT 1"))
                            return True
                    except Exception:
                        await asyncio.sleep(1)
                return False
            finally:
                await engine.dispose()

        if not asyncio.run(check_db()):
            raise RuntimeError("Test Postgres did not become ready in time; migrations were not run.")

        print("Waiting for Redis to be ready...")

        async def check_redis():
            redis_client = aioredis.from_url(settings.redis.url)
            try:
                for _ in range(10):
                    try:
                        if await redis_client.ping():
                            return True
                    except Exception:
                        await asyncio.sleep(1)
                return False
            finally:
                await redis_client.aclose()

        if not asyncio.run(check_redis()):
            raise RuntimeError("Test Redis did not become ready in time; migrations were not run.")

        print("Running migrations...")
        env = os.environ.copy()
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True, env=env)

        yield
    finally:
        if compose_started:
            try:
                subprocess.run([*compose_command, "down"], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print("\nWarning: Failed to auto-stop docker infrastructure.")


@pytest.fixture
async def app() -> AsyncGenerator[FastAPI, None]:
    """Yield a FastAPI application initialized with lifespan."""
    app_instance = create_app()
    async with LifespanManager(app_instance):
        yield app_instance


@pytest.fixture
async def db_session(app: FastAPI) -> AsyncGenerator:
    async with get_session() as session:
        yield session


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Yield an async httpx client connected to the test app."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
