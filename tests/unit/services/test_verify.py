import json
from unittest.mock import AsyncMock

import pytest

from src.domain.dtos.verify import VerifyCodeDTO
from src.domain.exceptions import CodeHasExpired, InvalidVerifyCode, UserEmailAlreadyExists
from src.services.verify import VerifyService


@pytest.fixture
def uow_mock():
    mock = AsyncMock()
    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None
    return mock


@pytest.fixture
def verify_service(uow_mock):
    return VerifyService(uow_mock)


@pytest.fixture
def verify_data():
    return VerifyCodeDTO(
        email="test@example.com",
        code=666666,
        verify_token="token123"
    )


@pytest.mark.asyncio
async def test_create_email_code_success(verify_service, uow_mock):
    email = "test@example.com"
    uow_mock.user_repository.get_by_email.return_value = None

    verify_token = await verify_service.create_email_code(email)

    assert verify_token is not None
    assert isinstance(verify_token, str)
    uow_mock.verify_repository.set_value.assert_called_once()
    args, kwargs = uow_mock.verify_repository.set_value.call_args
    assert kwargs["key"] == verify_token
    assert json.loads(kwargs["value"])["email"] == email
    assert json.loads(kwargs["value"])["code"] == 666666
    assert json.loads(kwargs["value"])["status"] == "pending"
    assert kwargs["exp"] == 5


@pytest.mark.asyncio
async def test_verify_email_code_success(verify_service, uow_mock, verify_data):
    uow_mock.user_repository.get_by_email.return_value = None

    redis_data = {
        "email": verify_data.email,
        "code": verify_data.code,
        "status": "pending"
    }
    uow_mock.verify_repository.get_value.return_value = json.dumps(redis_data)

    await verify_service.verify_email_code(verify_data)

    uow_mock.user_repository.get_by_email.assert_called_once_with(user_email=verify_data.email)
    uow_mock.verify_repository.get_value.assert_called_once_with(verify_data.verify_token)
    uow_mock.verify_repository.update_field.assert_called_once_with(
        key=verify_data.verify_token,
        field="status",
        value="verified",
        new_exp=24 * 60
    )


@pytest.mark.asyncio
async def test_verify_email_code_user_already_exists(verify_service, uow_mock, verify_data):
    uow_mock.user_repository.get_by_email.return_value = object()

    with pytest.raises(UserEmailAlreadyExists):
        await verify_service.verify_email_code(verify_data)

    uow_mock.user_repository.get_by_email.assert_called_once_with(user_email=verify_data.email)
    uow_mock.verify_repository.get_value.assert_not_called()


@pytest.mark.asyncio
async def test_verify_email_code_expired(verify_service, uow_mock, verify_data):
    uow_mock.user_repository.get_by_email.return_value = None
    uow_mock.verify_repository.get_value.return_value = None

    with pytest.raises(CodeHasExpired):
        await verify_service.verify_email_code(verify_data)


@pytest.mark.asyncio
async def test_verify_email_code_invalid_code(verify_service, uow_mock, verify_data):
    uow_mock.user_repository.get_by_email.return_value = None

    redis_data = {
        "email": verify_data.email,
        "code": 111111,
        "status": "pending"
    }
    uow_mock.verify_repository.get_value.return_value = json.dumps(redis_data)

    with pytest.raises(InvalidVerifyCode):
        await verify_service.verify_email_code(verify_data)


@pytest.mark.asyncio
async def test_verify_email_code_invalid_email(verify_service, uow_mock, verify_data):
    uow_mock.user_repository.get_by_email.return_value = None

    redis_data = {
        "email": "different@example.com",
        "code": verify_data.code,
        "status": "pending"
    }
    uow_mock.verify_repository.get_value.return_value = json.dumps(redis_data)

    with pytest.raises(InvalidVerifyCode):
        await verify_service.verify_email_code(verify_data)
