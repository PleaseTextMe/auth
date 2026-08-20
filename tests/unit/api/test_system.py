import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api.system import router


@pytest.fixture
async def test_app():
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return app

@pytest.fixture
async def test_client(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://testserver"
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_healthcheck(test_client):
    response = await test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
