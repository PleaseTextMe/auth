import logging
import secrets
from abc import ABC, abstractmethod
from collections.abc import Iterable
from uuid import UUID

from argon2.exceptions import VerifyMismatchError

from src.core.config import settings
from src.core.utils.hash import hash_token, password_hasher
from src.domain.dtos.session import SessionCreateDTO
from src.domain.entities.session import Session
from src.domain.exceptions import UserNotFound
from src.services.interfaces.uow import IUnitOfWork

logger = logging.getLogger(__name__)


class ISessionService(ABC):

    @abstractmethod
    async def create(self, session_data: SessionCreateDTO) -> str: ...

    @abstractmethod
    async def logout(self, auth_token_hash: str): ...


class SessionService(ISessionService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def create(self, session_data: SessionCreateDTO) -> str | None:
        async with self._uow as uow:
            user = await uow.user_repository.get_by_email(
                user_email=session_data.email
            )
            if not user:
                raise UserNotFound()

            try:
                hash_str = user.password_hash.decode("utf-8")
                password_hasher.verify(hash_str, session_data.password)
            except VerifyMismatchError:
                raise UserNotFound()

            auth_token = secrets.token_hex(32)
            session_data = Session.create(
                user_id=user.id,
                auth_token_hash=hash_token(auth_token),
                **session_data.model_dump(),
            )
            await uow.session_repository.create(session_data)
            return auth_token

    async def logout(self, auth_token_hash: str):
        async with self._uow as uow:
            await uow.session_repository.deactivate_token(
                auth_token_hash
            )
