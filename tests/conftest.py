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

from src.core.config import settings
from src.infrastructure.db.postgres import get_session
from src.main import create_app


@pytest.fixture(scope="session", autouse=True)
def setup_docker_infrastructure(request):  # noqa: C901
    """Start docker-compose and run migrations for tests."""
    has_integration = any(item.get_closest_marker("integration") for item in request.session.items)
    if not has_integration:
        yield
        return

    compose_file = "tests/docker-compose.test.yml"
    print("\nStarting test infrastructure...")
    try:
        subprocess.run(
            ["docker", "compose", "-f", compose_file, "up", "-d"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(
            f"\nWarning: Failed to auto-start docker infrastructure. Error:\n{e.stderr}\nMake sure to run 'sudo docker compose -f {compose_file} up -d' manually before running tests."
        )

    print("Waiting for Postgres to be ready...")

    engine = create_async_engine(settings.postgres.connection_url)

    async def check_db():
        for _ in range(10):
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    return True
            except Exception:
                await asyncio.sleep(1)
        return False

    is_ready = asyncio.run(check_db())
    if not is_ready:
        print("Warning: Postgres did not become ready in time.")

    print("Waiting for Redis to be ready...")

    async def check_redis():
        redis_client = aioredis.from_url(settings.redis.url)
        for _ in range(10):
            try:
                if await redis_client.ping():
                    await redis_client.aclose()
                    return True
            except Exception:
                await asyncio.sleep(1)
        await redis_client.aclose()
        return False

    is_redis_ready = asyncio.run(check_redis())
    if not is_redis_ready:
        print("Warning: Redis did not become ready in time.")

    print("Running migrations...")
    env = os.environ.copy()
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True, env=env)

    yield

    try:
        subprocess.run(
            ["docker", "compose", "-f", compose_file, "down"], check=True, capture_output=True
        )
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
