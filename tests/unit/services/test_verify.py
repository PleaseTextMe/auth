import json
from unittest.mock import AsyncMock, patch

import pytest

from src.domain.dtos.verify import VerifyCodeDTO
from src.domain.exceptions import CodeHasExpired, InvalidVerifyCode, UserEmailAlreadyExists
from src.services.verify import VerifyService


@pytest.fixture
def verify_service(mock_uow):
    return VerifyService(mock_uow)


@pytest.fixture
def verify_data():
    return VerifyCodeDTO(email="hopso@kto.pID", code=666666, verify_token="token123")


@pytest.mark.asyncio
async def test_create_email_code_success(verify_service, mock_uow):
    email = "hopso@kto.pID"

    mock_uow.user_repository.get_by_email.return_value = None
    with patch("src.services.verify.send_verification_email", new_callable=AsyncMock) as delivery:
        verify_token = await verify_service.create_email_code(email)

    assert verify_token is not None
    assert isinstance(verify_token, str)
    mock_uow.verify_repository.set_value.assert_called_once()
    args, kwargs = mock_uow.verify_repository.set_value.call_args
    assert kwargs["key"] == verify_token
    assert json.loads(kwargs["value"])["email"] == email
    code = json.loads(kwargs["value"])["code"]
    assert 100000 <= code <= 999999
    delivery.assert_awaited_once_with(email, code)
    assert json.loads(kwargs["value"])["status"] == "pending"
    assert kwargs["exp"] == 5


@pytest.mark.asyncio
async def test_verify_email_code_success(verify_service, mock_uow, verify_data):
    mock_uow.user_repository.get_by_email.return_value = None

    mock_uow.verify_repository.verify_code.return_value = 1

    await verify_service.verify_email_code(verify_data)

    mock_uow.user_repository.get_by_email.assert_called_once_with(user_email=verify_data.email)
    mock_uow.verify_repository.verify_code.assert_awaited_once_with(
        verify_data.verify_token, str(verify_data.email), verify_data.code
    )



@pytest.mark.asyncio
async def test_verify_email_code_user_already_exists(verify_service, mock_uow, verify_data):
    mock_uow.user_repository.get_by_email.return_value = object()

    with pytest.raises(UserEmailAlreadyExists):
        await verify_service.verify_email_code(verify_data)

    mock_uow.user_repository.get_by_email.assert_called_once_with(user_email=verify_data.email)
    mock_uow.verify_repository.verify_code.assert_not_called()


@pytest.mark.asyncio
async def test_verify_email_code_expired(verify_service, mock_uow, verify_data):
    mock_uow.user_repository.get_by_email.return_value = None
    mock_uow.verify_repository.verify_code.return_value = -1

    with pytest.raises(CodeHasExpired):
        await verify_service.verify_email_code(verify_data)


@pytest.mark.asyncio
async def test_verify_email_code_invalid_code(verify_service, mock_uow, verify_data):
    mock_uow.user_repository.get_by_email.return_value = None

    mock_uow.verify_repository.verify_code.return_value = 0

    with pytest.raises(InvalidVerifyCode):
        await verify_service.verify_email_code(verify_data)


@pytest.mark.asyncio
async def test_verify_email_code_invalid_email(verify_service, mock_uow, verify_data):
    mock_uow.user_repository.get_by_email.return_value = None

    mock_uow.verify_repository.verify_code.return_value = 0

    with pytest.raises(InvalidVerifyCode):
        await verify_service.verify_email_code(verify_data)
