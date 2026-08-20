import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.api.v1.router import router
from src.services.user import IUserService


@pytest.fixture
async def test_app(mock_user_service):
    app = FastAPI()
    app.include_router(router, prefix="/api")

    class MockProvider(Provider):
        @provide(scope=Scope.APP)
        def get_user_service(self) -> IUserService:
            return mock_user_service

    container = make_async_container(MockProvider())
    setup_dishka(container=container, app=app)
    yield app
    await container.close()


@pytest.mark.asyncio
async def test_get_all_users(test_client, mock_user_service, valid_user):
    mock_user_service.get_all.return_value = [valid_user]
    response = await test_client.get("/api/v1/users/")
    assert response.status_code == 200
    assert response.json() == [{"username": "testuser", "public_bundle": {"key": "val"}}]
    mock_user_service.get_all.assert_called_once()
