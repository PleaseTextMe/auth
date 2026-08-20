import logging
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from src.core.utils.hash import hash_token
from src.domain.entities.session import Session
from src.domain.entities.user import User
from src.services.interfaces.uow import IUnitOfWork

logger = logging.getLogger(__name__)

auth_scheme = APIKeyHeader(name="x-auth-token", auto_error=False)


@inject
async def get_current_session(
    uow: FromDishka[IUnitOfWork],
    auth_token: str | None = Depends(auth_scheme),
) -> Session:
    """
    Извлекает токен, хеширует его и проверяет статус сессии в БД.
    """
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходимо авторизоваться"
        )

    token_hash = hash_token(auth_token)

    async with uow as current_uow:
        session = await current_uow.session_repository.get_by_hash(token_hash)

        if not session:
            logger.warning("Попытка входа с несуществующим токеном")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Сессия не найдена или недействительна"
            )

        if not session.is_active:
            logger.info(f"Попытка использования деактивированной сессии: {session.id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Сессия завершена"
            )

        return session


@inject
async def get_current_user(
    request: Request,
    uow: FromDishka[IUnitOfWork],
    session: Session = Depends(get_current_session),
) -> User:
    """
    Получает пользователя по активной сессии и проверяет его статус.
    """
    async with uow as current_uow:
        user = await current_uow.user_repository.get_by_id(session.user_id)

        if not user:
            logger.error(f"Сессия {session.id} ссылается на удаленного пользователя {session.user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )

        if getattr(user, "is_active", True) is False:
            logger.warning(f"Заблокированный пользователь {user.id} пытается получить доступ")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Аккаунт заблокирован"
            )

        return user


CurrentSessionDep = Annotated[Session, Depends(get_current_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
