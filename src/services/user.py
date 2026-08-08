import json
import logging
from abc import ABC, abstractmethod

from src.core.utils.hash import password_hasher
from src.domain.dtos.user import (
    UserCreateDatabaseDTO,
    UserCreateDTO,
)
from src.domain.entities.user import User
from src.domain.exceptions import (
    UserEmailAlreadyExists,
    UsernameAlreadyExists,
    VerifyCodeNotConfirmed,
)
from src.services.interfaces.uow import IUnitOfWork

logger = logging.getLogger(__name__)


class IUserService(ABC):

    @abstractmethod
    async def create(self, user_data: UserCreateDTO) -> User: ...

    @abstractmethod
    async def get_all(self) -> list[User]: ...


class UserService(IUserService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def create(self, user_data: UserCreateDTO) -> User:
        async with self._uow as uow:
            if await uow.user_repository.get_by_email(
                user_email=user_data.email
            ):
                raise UserEmailAlreadyExists()

            redis_data = await uow.verify_repository.get_value(
                user_data.verify_token
            )

            if (
                not redis_data or
                json.loads(redis_data)["status"] != "verified"
            ):
                raise VerifyCodeNotConfirmed()

            await uow.verify_repository.delete_value(user_data.verify_token)

            if await uow.user_repository.get_by_username(
                username=user_data.username
            ):
                raise UsernameAlreadyExists()

            hashed_password = password_hasher.hash(user_data.password).encode("utf-8")
            user_dict = user_data.model_dump(exclude={"password"})
            user_data = UserCreateDatabaseDTO(
                password_hash=hashed_password,
                **user_dict
            )
            return await uow.user_repository.create(user_data)

    async def get_all(self) -> list[User]:
        async with self._uow as uow:
            return await uow.user_repository.get_all()

