import logging
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config import settings
from src.domain.entities.token import Token
from src.domain.entities.user import User
from src.domain.exceptions import (
    Forbidden,
    SessionHasExpired,
    UserNotFound,
)
from src.services.blacklist import IBlacklistService
from src.services.jwt import IJWTService
from src.services.user import IUserService

auth_scheme = HTTPBearer(auto_error=False)

logger = logging.getLogger(__name__)


def set_refresh_token(response: Response, refresh_token: str) -> None:
    """
    Устанавливает refresh-токен в cookies ответа.
    """
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.service.debug,
        samesite="Strict",
        max_age=settings.service.refresh_token_expire,
    )


def get_refresh_token(request: Request) -> str:
    """
    Извлекает refresh-токен из cookies.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        logger.warning("Refresh токен не обнаружен в cookies")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh токен не обнаружен"
        )
    request.state.refresh_token = refresh_token
    return refresh_token


@inject
async def get_refresh_token_data(
    request: Request,
    jwt_service: FromDishka[IJWTService],
    refresh_token: str = Depends(get_refresh_token),
) -> Token:
    """
    Декодирует refresh-токен и сохраняет его данные.
    """
    try:
        payload: Token = jwt_service.decode_token(refresh_token)
        request.state.payload = payload
        return payload
    except Exception as e:
        if isinstance(e, SessionHasExpired):
            raise
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен"
        ) from e


@inject
async def get_current_user(
    user_repository: FromDishka[IUserService],
    payload: Token = Depends(get_refresh_token_data),
) -> User:
    """
    Получает пользователя из базы по ID из refresh-токена.
    """
    user: User | None = await user_repository.get_by_id(payload.user_id)
    if not user:
        logger.error(f"Ошибка при получении пользователя с id {payload.user_id} из БД")
        raise UserNotFound()
    return user


@inject
async def get_access_token_data(
    request: Request,
    jwt_service: FromDishka[IJWTService],
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Token:
    """
    Извлекает и декодирует access-токен.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться"
        )
    
    access_token = credentials.credentials
    try:
        payload: Token = jwt_service.decode_token(access_token)
        request.state.access_token_payload = payload
        return payload
    except Exception as e:
        if isinstance(e, SessionHasExpired):
            raise
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен"
        ) from e


def require_permissions(required_permissions: list[str] | None = None):
    """
    Фабрика зависимостей для проверки прав на основе access-токена.
    """

    @inject
    async def check_permission(
        request: Request,
        jwt_service: FromDishka[IJWTService],
        blacklist_service: FromDishka[IBlacklistService],
        credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ) -> Token:
        logger.debug("Проверяем access-токен и права доступа...")
        
        if credentials is None or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться"
            )

        access_token = credentials.credentials

        try:
            payload: Token = jwt_service.decode_token(access_token)

            # Проверка токена в черном списке
            if await blacklist_service.is_exists(payload.jti):
                raise SessionHasExpired()

            # Проверка необходимых прав
            if required_permissions and not set(required_permissions).issubset(set(payload.scope)):
                raise Forbidden()

            request.state.user = payload.user_id
            return payload

        except Exception as e:
            if isinstance(e, (SessionHasExpired, Forbidden)):
                raise
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен"
            ) from e

    return check_permission


CurrentUserDep = Annotated[User, Depends(get_current_user)]
AccessTokenDep = Annotated[Token, Depends(get_access_token_data)]
