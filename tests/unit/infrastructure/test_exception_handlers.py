from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, Request

from src.domain.exceptions import (
    UserEmailAlreadyExists,
    UsernameAlreadyExists,
    UserNotFound,
    VerifyCodeNotConfirmed,
)
from src.infrastructure.handlers.exceptions import exception_handlers


@pytest.fixture
def mock_request():
    return AsyncMock(spec=Request)


@pytest.mark.asyncio
async def test_exception_handler_user_not_found(mock_request):
    handler = exception_handlers[UserNotFound]
    exc = UserNotFound()

    with pytest.raises(HTTPException) as exc_info:
        await handler(mock_request, exc)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Пользователь не найден."


@pytest.mark.asyncio
async def test_exception_handler_email_already_exists(mock_request):
    handler = exception_handlers[UserEmailAlreadyExists]
    exc = UserEmailAlreadyExists()

    with pytest.raises(HTTPException) as exc_info:
        await handler(mock_request, exc)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Пользователь с таким email уже существует."


@pytest.mark.asyncio
async def test_exception_handler_username_already_exists(mock_request):
    handler = exception_handlers[UsernameAlreadyExists]
    exc = UsernameAlreadyExists()

    with pytest.raises(HTTPException) as exc_info:
        await handler(mock_request, exc)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Пользователь с таким username уже существует."


@pytest.mark.asyncio
async def test_exception_handler_verify_code_not_confirmed(mock_request):
    handler = exception_handlers[VerifyCodeNotConfirmed]
    exc = VerifyCodeNotConfirmed()

    with pytest.raises(HTTPException) as exc_info:
        await handler(mock_request, exc)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Проверочный код не подтвержден."
