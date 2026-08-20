
import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import Depends, FastAPI

from src.api.v1.depends import get_current_session, get_current_user
from src.domain.entities.session import Session
from src.domain.entities.user import User
from src.services.interfaces.uow import IUnitOfWork


@pytest.fixture
async def test_app(mock_uow):
    app = FastAPI()

    @app.get("/session/")
    async def get_session(session: Session = Depends(get_current_session)):
        return {"id": session.id}

    @app.get("/user/")
    async def get_user(user: User = Depends(get_current_user)):
        return {"id": user.id}

    class MockProvider(Provider):
        @provide(scope=Scope.APP)
        def get_uow(self) -> IUnitOfWork:
            return mock_uow

    container = make_async_container(MockProvider())
    setup_dishka(container=container, app=app)
    yield app
    await container.close()


@pytest.mark.asyncio
async def test_get_current_session_success(test_client, mock_uow, valid_session):
    mock_uow.session_repository.get_by_hash.return_value = valid_session
    response = await test_client.get("/session/", headers={"x-auth-token": "valid_token"})
    assert response.status_code == 200
    assert response.json() == {"id": 1}


@pytest.mark.asyncio
async def test_get_current_session_no_token(test_client):
    response = await test_client.get("/session/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Необходимо авторизоваться"


@pytest.mark.asyncio
async def test_get_current_session_not_found(test_client, mock_uow):
    mock_uow.session_repository.get_by_hash.return_value = None
    response = await test_client.get("/session/", headers={"x-auth-token": "invalid_token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Сессия не найдена или недействительна"


@pytest.mark.asyncio
async def test_get_current_session_inactive(test_client, mock_uow, valid_session):
    valid_session.is_active = False
    mock_uow.session_repository.get_by_hash.return_value = valid_session
    response = await test_client.get("/session/", headers={"x-auth-token": "invalid_token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Сессия завершена"


@pytest.mark.asyncio
async def test_get_current_user_success(test_client, mock_uow, valid_session, valid_user):
    mock_uow.session_repository.get_by_hash.return_value = valid_session
    mock_uow.user_repository.get_by_id.return_value = valid_user
    response = await test_client.get("/user/", headers={"x-auth-token": "valid_token"})
    assert response.status_code == 200
    assert response.json() == {"id": 1}


@pytest.mark.asyncio
async def test_get_current_user_not_found(test_client, mock_uow, valid_session):
    mock_uow.session_repository.get_by_hash.return_value = valid_session
    mock_uow.user_repository.get_by_id.return_value = None
    response = await test_client.get("/user/", headers={"x-auth-token": "valid_token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Пользователь не найден"


@pytest.mark.asyncio
async def test_get_current_user_inactive(test_client, mock_uow, valid_session, valid_user):
    valid_user.is_active = False
    mock_uow.session_repository.get_by_hash.return_value = valid_session
    mock_uow.user_repository.get_by_id.return_value = valid_user
    response = await test_client.get("/user/", headers={"x-auth-token": "valid_token"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Аккаунт заблокирован"
