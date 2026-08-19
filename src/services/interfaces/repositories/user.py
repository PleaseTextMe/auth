import abc

from pydantic import EmailStr

from src.domain.dtos.user import (
    UserCreateDatabaseDTO,
)
from src.domain.entities.user import User


class IUserRepository(abc.ABC):

    @abc.abstractmethod
    async def create(self, user_data: UserCreateDatabaseDTO) -> User: ...

    @abc.abstractmethod
    async def get_by_email(self, user_email: EmailStr) -> User | None: ...

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abc.abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abc.abstractmethod
    async def get_all(self) -> list[User]: ...

