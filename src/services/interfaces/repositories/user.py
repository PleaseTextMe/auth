import abc
from collections.abc import Iterable
from uuid import UUID

# from src.domain.dtos.address import AddressCreateDTO, AddressUpdateDTO
from src.domain.entities.user import User, UserSalt


class IUserRepository(abc.ABC):
    # @abc.abstractmethod
    # async def create(self, address: AddressCreateDTO) -> Address: ...

    @abc.abstractmethod
    async def get_salt(self, user_email: str) -> UserSalt | None: ...

    # @abc.abstractmethod
    # async def get_my_addresses(self, user_id: UUID) -> Iterable[Address]: ...

    # @abc.abstractmethod
    # async def delete(self, address_id: UUID) -> Address | None: ...

    # @abc.abstractmethod
    # async def update(self, address: AddressUpdateDTO, address_id: UUID) -> Address | None: ...

    # @abc.abstractmethod
    # async def get_nearby_addresses(self, latitude: float, longitude: float, radius: float = 3_000.0) -> Iterable[Address]: ...
