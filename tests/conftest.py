import asyncio
import os
import subprocess
import time
from typing import AsyncGenerator

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from src.main import create_app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def setup_docker_infrastructure(request):
    """Start docker-compose and run migrations for tests."""
    has_integration = any(item.get_closest_marker("integration") for item in request.session.items)
    if not has_integration:
        yield
        return
    
    if os.environ.get("MOCK_EXTERNAL_API"):
        yield
        return
    
    compose_file = "tests/docker-compose.test.yml"
    print("\nStarting test infrastructure...")
    try:
        subprocess.run(["docker", "compose", "-f", compose_file, "up", "-d"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"\nWarning: Failed to auto-start docker infrastructure. Error:\n{e.stderr}\nMake sure to run 'sudo docker compose -f {compose_file} up -d' manually before running tests.")

    
    print("Waiting for Postgres to be ready...")
    time.sleep(3) # Wait for db to accept connections
    
    print("Running migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    
    yield
    
    try:
        subprocess.run(["docker", "compose", "-f", compose_file, "down"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("\nWarning: Failed to auto-stop docker infrastructure.")

@pytest.fixture(scope="session")
async def app() -> AsyncGenerator[FastAPI, None]:
    """Yield a FastAPI application initialized with lifespan."""
    app_instance = create_app()
    async with LifespanManager(app_instance):
        yield app_instance

@pytest.fixture(scope="session")
async def client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Yield an async httpx client connected to the test app."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
