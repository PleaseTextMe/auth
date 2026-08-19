import json
from unittest.mock import AsyncMock

import pytest

from src.domain.dtos.user import UserCreateDTO
from src.domain.entities.user import User
from src.domain.exceptions import (
    UserEmailAlreadyExists,
    UsernameAlreadyExists,
    VerifyCodeNotConfirmed,
)
from src.services.user import UserService


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.user_repository = AsyncMock()
    uow.verify_repository = AsyncMock()
    # Support async context manager
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def user_service(mock_uow):
    return UserService(uow=mock_uow)


@pytest.fixture
def valid_user_data():
    return UserCreateDTO(
        email="test@example.com",
        username="testuser",
        password="password123",
        verify_token="token123",
        public_bundle={"bundle_json": "{}", "signature": "sig"},
        vault={"encrypted_payload": "enc", "nonce": "nonce", "auth_tag": "tag"},
    )


@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_uow, valid_user_data):
    mock_uow.user_repository.get_by_email.return_value = None
    mock_uow.user_repository.get_by_username.return_value = None
    mock_uow.verify_repository.get_value.return_value = json.dumps({"status": "verified"})

    expected_user = User(
        id=1,
        email=valid_user_data.email,
        username=valid_user_data.username,
        password_hash=b"hashed_pass",
        public_bundle={"bundle_json": "{}", "signature": "sig"},
        vault={"encrypted_payload": "enc", "nonce": "nonce", "auth_tag": "tag"},
        is_active=True,
    )
    mock_uow.user_repository.create.return_value = expected_user

    result = await user_service.create(valid_user_data)

    assert result == expected_user
    mock_uow.user_repository.get_by_email.assert_called_once_with(user_email=valid_user_data.email)
    mock_uow.verify_repository.get_value.assert_called_once_with(valid_user_data.verify_token)
    mock_uow.verify_repository.delete_value.assert_called_once_with(valid_user_data.verify_token)
    mock_uow.user_repository.get_by_username.assert_called_once_with(
        username=valid_user_data.username
    )
    mock_uow.user_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_email_exists(user_service, mock_uow, valid_user_data):
    mock_uow.user_repository.get_by_email.return_value = User(
        id=1,
        email="test@example.com",
        username="a",
        password_hash=b"a",
        public_bundle={},
        vault={},
        is_active=True,
    )

    with pytest.raises(UserEmailAlreadyExists):
        await user_service.create(valid_user_data)

    mock_uow.verify_repository.get_value.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_verify_not_confirmed(user_service, mock_uow, valid_user_data):
    mock_uow.user_repository.get_by_email.return_value = None
    mock_uow.verify_repository.get_value.return_value = json.dumps({"status": "pending"})

    with pytest.raises(VerifyCodeNotConfirmed):
        await user_service.create(valid_user_data)


@pytest.mark.asyncio
async def test_create_user_username_exists(user_service, mock_uow, valid_user_data):
    mock_uow.user_repository.get_by_email.return_value = None
    mock_uow.verify_repository.get_value.return_value = json.dumps({"status": "verified"})
    mock_uow.user_repository.get_by_username.return_value = User(
        id=1,
        email="a@a.com",
        username="testuser",
        password_hash=b"a",
        public_bundle={},
        vault={},
        is_active=True,
    )

    with pytest.raises(UsernameAlreadyExists):
        await user_service.create(valid_user_data)


@pytest.mark.asyncio
async def test_get_all_users(user_service, mock_uow):
    expected_users = [
        User(
            id=1,
            email="a@a.com",
            username="a",
            password_hash=b"a",
            public_bundle={},
            vault={},
            is_active=True,
        )
    ]
    mock_uow.user_repository.get_all.return_value = expected_users

    result = await user_service.get_all()

    assert result == expected_users
    mock_uow.user_repository.get_all.assert_called_once()
