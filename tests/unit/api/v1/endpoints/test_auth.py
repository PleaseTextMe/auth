from unittest.mock import AsyncMock

import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api.v1.depends import get_current_session, get_current_user
from src.api.v1.router import router
from src.domain.entities.session import Session
from src.domain.entities.user import User
from src.services.session import ISessionService
from src.services.user import IUserService
from src.services.verify import IVerifyService


@pytest.fixture
async def mock_user_service():
    service = AsyncMock(spec=IUserService)
    return service


@pytest.fixture
async def mock_session_service():
    service = AsyncMock(spec=ISessionService)
    service.create.return_value = "mock_auth_token"
    return service


@pytest.fixture
async def mock_verify_service():
    service = AsyncMock(spec=IVerifyService)
    service.create_email_code.return_value = "mock_verify_token"
    return service


@pytest.fixture
def mock_session():
    return Session(
        id=1,
        user_id=1,
        auth_token_hash=b"hash",
        user_agent="agent",
        user_ip="ip",
        device_type="web",
        is_active=True,
    )


@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="axel@harlem.hui",
        username="testuser",
        password_hash="hash",
        public_bundle={"key": "val"},
        vault={"key": "val"},
        is_active=True,
    )


@pytest.fixture
async def test_app(
    mock_user_service, mock_session_service, mock_verify_service, mock_session, mock_user
):
    app = FastAPI()
    app.include_router(router, prefix="/api")

    class MockProvider(Provider):
        @provide(scope=Scope.APP)
        def get_user_service(self) -> IUserService:
            return mock_user_service

        @provide(scope=Scope.APP)
        def get_session_service(self) -> ISessionService:
            return mock_session_service

        @provide(scope=Scope.APP)
        def get_verify_service(self) -> IVerifyService:
            return mock_verify_service

    container = make_async_container(MockProvider())
    setup_dishka(container=container, app=app)

    app.dependency_overrides[get_current_session] = lambda: mock_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    yield app
    await container.close()


@pytest.fixture
async def test_client(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register(test_client, mock_user_service, mock_session_service):
    payload = {
        "email": "axel@harlem.hui",
        "username": "testuser",
        "password": "windows_wanna_suck",
        "verify_token": "token",
        "public_bundle": {"bundle_json": "{}", "signature": "sig"},
        "vault": {"encrypted_payload": "enc", "nonce": "nonce", "auth_tag": "tag"},
    }
    response = await test_client.post(
        "/api/v1/auth/register/", json=payload, headers={"user-agent": "HelloToPavelDurov", "host": "127.0.0.1"}
    )
    assert response.status_code == 201
    assert response.json() == {"auth_token": "mock_auth_token"}
    mock_user_service.create.assert_called_once()
    mock_session_service.create.assert_called_once()


@pytest.mark.asyncio
async def test_login(test_client, mock_session_service):
    payload = {"email": "axel@harlem.hui", "password": "windows_wanna_suck"}
    response = await test_client.post(
        "/api/v1/auth/login/", json=payload, headers={"user-agent": "HelloToPavelDurov", "host": "127.0.0.1"}
    )
    assert response.status_code == 200
    assert response.json() == {"auth_token": "mock_auth_token"}
    mock_session_service.create.assert_called_once()


@pytest.mark.asyncio
async def test_send_verify_code(test_client, mock_verify_service):
    payload = {"email": "axel@harlem.hui"}
    response = await test_client.post("/api/v1/auth/send-verify-code/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"verify_token": "mock_verify_token"}
    mock_verify_service.create_email_code.assert_called_once_with("axel@harlem.hui")


@pytest.mark.asyncio
async def test_check_verify_code(test_client, mock_verify_service):
    payload = {"email": "axel@harlem.hui", "code": "123456", "verify_token": "token"}
    response = await test_client.post("/api/v1/auth/check-verify-code/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"is_verified": True}
    mock_verify_service.verify_email_code.assert_called_once()


@pytest.mark.asyncio
async def test_logout(test_client, mock_session_service, mock_session):
    response = await test_client.post("/api/v1/auth/logout/")
    assert response.status_code == 204
    mock_session_service.logout.assert_called_once_with(mock_session.auth_token_hash)


@pytest.mark.asyncio
async def test_get_me(test_client):
    response = await test_client.get("/api/v1/auth/me/")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_my_session_info(test_client):
    response = await test_client.get("/api/v1/auth/my-session/")
    assert response.status_code == 200
    assert response.json()["id"] == 1
