from unittest.mock import AsyncMock

import pytest

from src.core.utils.hash import password_hasher
from src.domain.dtos.session import SessionCreateDTO
from src.domain.entities.user import User
from src.domain.exceptions import UserNotFound
from src.services.session import SessionService


@pytest.fixture
def uow_mock():
    mock = AsyncMock()
    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None
    return mock


@pytest.fixture
def session_service(uow_mock):
    return SessionService(uow_mock)


@pytest.fixture
def valid_password():
    return "AxelUsingArchBTW123321"


@pytest.fixture
def user_mock(valid_password):
    return User.create(
        username="testuser",
        email="test@example.com",
        password_hash=password_hasher.hash(valid_password).encode("utf-8"),
        public_bundle={},
        vault={},
        is_active=True
    )


@pytest.fixture
def session_data(valid_password):
    return SessionCreateDTO(
        email="test@example.com",
        password=valid_password,
        user_agent="test-agent",
        user_ip="127.0.0.1",
        device_type="test-device"
    )


@pytest.mark.asyncio
async def test_create_session_success(session_service, uow_mock, session_data, user_mock):
    uow_mock.user_repository.get_by_email.return_value = user_mock
    uow_mock.session_repository.create.return_value = None

    auth_token = await session_service.create(session_data)

    assert auth_token is not None
    assert isinstance(auth_token, str)
    uow_mock.user_repository.get_by_email.assert_called_once_with(user_email=session_data.email)
    uow_mock.session_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_session_user_not_found(session_service, uow_mock, session_data):
    uow_mock.user_repository.get_by_email.return_value = None

    with pytest.raises(UserNotFound):
        await session_service.create(session_data)

    uow_mock.user_repository.get_by_email.assert_called_once_with(user_email=session_data.email)
    uow_mock.session_repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_session_invalid_password(session_service, uow_mock, session_data, user_mock):
    session_data.password = "WrongPassword!"
    uow_mock.user_repository.get_by_email.return_value = user_mock

    with pytest.raises(UserNotFound):
        await session_service.create(session_data)

    uow_mock.user_repository.get_by_email.assert_called_once_with(user_email=session_data.email)
    uow_mock.session_repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_logout_success(session_service, uow_mock):
    auth_token_hash = "some_hash"

    await session_service.logout(auth_token_hash)

    uow_mock.session_repository.deactivate_token.assert_called_once_with(auth_token_hash)
