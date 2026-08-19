import asyncio
import subprocess
import time
from typing import AsyncGenerator

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from src.main import create_app


@pytest.fixture(scope="session", autouse=True)
def setup_docker_infrastructure(request):
    """Start docker-compose and run migrations for tests."""
    has_integration = any(item.get_closest_marker("integration") for item in request.session.items)
    if not has_integration:
        yield
        return



    compose_file = "tests/docker-compose.test.yml"
    print("\nStarting test infrastructure...")
    try:
        subprocess.run(["docker", "compose", "-f", compose_file, "up", "-d"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"\nWarning: Failed to auto-start docker infrastructure. Error:\n{e.stderr}\nMake sure to run 'sudo docker compose -f {compose_file} up -d' manually before running tests.")


    print("Waiting for Postgres to be ready...")
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    import asyncio
    
    engine = create_async_engine("postgresql+asyncpg://test_user:test_password@localhost:5435/please_text_me_test_db")
    
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

    print("Running migrations...")
    import sys
    import os
    env = os.environ.copy()
    env["POSTGRES_USER"] = "test_user"
    env["POSTGRES_PASSWORD"] = "test_password"
    env["POSTGRES_DB"] = "please_text_me_test_db"
    env["POSTGRES_HOST"] = "localhost"
    env["POSTGRES_PORT"] = "5435"
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True, env=env)

    yield

    try:
        subprocess.run(["docker", "compose", "-f", compose_file, "down"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("\nWarning: Failed to auto-stop docker infrastructure.")

@pytest.fixture
async def app() -> AsyncGenerator[FastAPI, None]:
    """Yield a FastAPI application initialized with lifespan."""
    app_instance = create_app()
    async with LifespanManager(app_instance):
        yield app_instance

@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Yield an async httpx client connected to the test app."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
