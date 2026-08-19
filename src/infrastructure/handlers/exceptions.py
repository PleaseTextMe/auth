from collections.abc import Callable, Coroutine
from typing import Any, NoReturn

from fastapi import HTTPException, Request, Response, status

from src.domain.exceptions import (
    CodeHasExpired,
    Forbidden,
    InvalidVerifyCode,
    SessionHasExpired,
    UserEmailAlreadyExists,
    UsernameAlreadyExists,
    UserNotFound,
    VerifyCodeNotConfirmed,
)


def create_exception_handler(
    status_code: int, detail: str
) -> Callable[[Request, Any], Coroutine[Any, Any, Response]]:
    """
    Фабрика для создания исключений
    :param status_code: код статуса
    :param detail: текст ошибки
    :return: HTTPException
    """

    async def handler(request: Request, exc: Exception) -> NoReturn:
        raise HTTPException(status_code=status_code, detail=detail)

    return handler


exception_handlers: dict[
    type[Exception], Callable[[Request, Any], Coroutine[Any, Any, Response]]
] = {
    Forbidden: create_exception_handler(
        status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для выполнения операции."
    ),
    InvalidVerifyCode: create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный код."
    ),
    SessionHasExpired: create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия устарела или была завершена."
    ),
    UserNotFound: create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден."
    ),
    UserEmailAlreadyExists: create_exception_handler(
        status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким email уже существует."
    ),
    UsernameAlreadyExists: create_exception_handler(
        status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким username уже существует."
    ),
    VerifyCodeNotConfirmed: create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Проверочный код не подтвержден."
    ),
    CodeHasExpired: create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Код был просрочен."
    ),
}
