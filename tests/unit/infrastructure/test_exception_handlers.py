import json

import pytest

from src.domain.exceptions import (
    UserEmailAlreadyExists,
    UsernameAlreadyExists,
    UserNotFound,
    VerifyCodeNotConfirmed,
)
from src.infrastructure.handlers.exceptions import exception_handlers


@pytest.mark.asyncio
async def test_exception_handler_user_not_found(mock_request):
    handler = exception_handlers[UserNotFound]
    exc = UserNotFound()

    response = await handler(mock_request, exc)

    assert response.status_code == 404
    assert json.loads(response.body)["detail"] == "Пользователь не найден."


@pytest.mark.asyncio
async def test_exception_handler_email_already_exists(mock_request):
    handler = exception_handlers[UserEmailAlreadyExists]
    exc = UserEmailAlreadyExists()

    response = await handler(mock_request, exc)

    assert response.status_code == 409
    assert json.loads(response.body)["detail"] == "Пользователь с таким email уже существует."


@pytest.mark.asyncio
async def test_exception_handler_username_already_exists(mock_request):
    handler = exception_handlers[UsernameAlreadyExists]
    exc = UsernameAlreadyExists()

    response = await handler(mock_request, exc)

    assert response.status_code == 409
    assert json.loads(response.body)["detail"] == "Пользователь с таким username уже существует."


@pytest.mark.asyncio
async def test_exception_handler_verify_code_not_confirmed(mock_request):
    handler = exception_handlers[VerifyCodeNotConfirmed]
    exc = VerifyCodeNotConfirmed()

    response = await handler(mock_request, exc)

    assert response.status_code == 400
    assert json.loads(response.body)["detail"] == "Проверочный код не подтвержден."
