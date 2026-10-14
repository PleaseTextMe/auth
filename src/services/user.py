import json
import logging
from abc import ABC, abstractmethod

from src.core.metrics import AUTH_REGISTRATIONS
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
    async def get_auth_version(self, email: str) -> int: ...

    @abstractmethod
    async def create(self, user_data: UserCreateDTO) -> User: ...

    @abstractmethod
    async def get_all(self) -> list[User]: ...


class UserService(IUserService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def get_auth_version(self, email: str) -> int:
        async with self._uow as uow:
            user = await uow.user_repository.get_by_email(user_email=email)
            return user.vault.get("auth_version", 1) if user else 2

    async def create(self, user_data: UserCreateDTO) -> User:
        async with self._uow as uow:
            if await uow.user_repository.get_by_email(
                user_email=user_data.email
            ):
                AUTH_REGISTRATIONS.labels(status="failed").inc()
                raise UserEmailAlreadyExists()

            redis_data = await uow.verify_repository.get_value(
                user_data.verify_token
            )

            verification = json.loads(redis_data) if redis_data else {}
            if (
                verification.get("status") != "verified"
                or verification.get("email") != user_data.email
            ):
                AUTH_REGISTRATIONS.labels(status="failed").inc()
                raise VerifyCodeNotConfirmed()

            if await uow.user_repository.get_by_username(
                username=user_data.username
            ):
                AUTH_REGISTRATIONS.labels(status="failed").inc()
                raise UsernameAlreadyExists()

            hashed_password = password_hasher.hash(user_data.password).encode("utf-8")
            user_dict = user_data.model_dump(exclude={"password"})
            user_data = UserCreateDatabaseDTO(
                password_hash=hashed_password,
                **user_dict
            )
            user = await uow.user_repository.create(user_data)
        # Preserve verification if the insert or commit fails. Database unique
        # constraints prevent concurrent registrations for the same email.
        await self._uow.verify_repository.delete_value(user_dict["verify_token"])
        AUTH_REGISTRATIONS.labels(status="success").inc()
        return user

    async def get_all(self) -> list[User]:
        async with self._uow as uow:
            return await uow.user_repository.get_all()

