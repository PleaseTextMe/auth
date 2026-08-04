import logging
import hmac
import hashlib
from abc import ABC, abstractmethod
from collections.abc import Iterable
from uuid import UUID

from src.domain.dtos.user import UserCreateDTO, AddressUpdateDTO
from src.domain.entities.user import User, UserSalt
# from src.services.exceptions import AddressNotFoundError, ForbiddenError
from src.services.interfaces.uow import IUnitOfWork
from src.core.config import settings

logger = logging.getLogger(__name__)


class IUserService(ABC):

    @abstractmethod
    async def get_salt_by_email(self, user_email: str) -> UserSalt: ...

    @abstractmethod
    async def create_user(self, user_email: str) -> User: ...

    @abstractmethod
    async def check_user_password(self, user_email: str) -> UserSalt: ...


class UserService(IUserService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def get_salt_by_email(self, user_email: str) -> UserSalt:
        alt_salt = hmac.new(
            key=settings.service.secret.encode("utf-8"),
            msg=user_email.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()[:32]
        alt_salt = UserSalt(kdf_salt=alt_salt)
        async with self._uow as uow:
            return await uow.user_repository.get_salt(user_email) or alt_salt

    # async def get_address_by_id(self, address_id: UUID, user_id: UUID) -> Address:
    #     """
    #     Получает адрес по id.
    #     :param address_id: ID адреса.
    #     :return: Адрес.
    #     """

    #     async with self._uow as uow:
    #         address = await uow.address_repository.get_address(address_id=address_id)
    #         if address is None:
    #             logger.warning("Адрес с id=%s не найден", address_id)
    #             raise AddressNotFoundError("Адрес не найден")
    #         if address.user_id != user_id:
    #             logger.warning("Адрес с id=%s не принадлежит пользователю с id=%s", address_id, user_id)
    #             raise ForbiddenError("Адрес не принадлежит пользователю")
    #         return address

    # async def get_my_addresses(self, user_id: UUID) -> Iterable[Address]:
    #     """
    #     Получает все адреса пользователя.
    #     :param user_id: ID пользователя.
    #     :return: Список адресов.
    #     """

    #     async with self._uow as uow:
    #         addresses = await uow.address_repository.get_my_addresses(user_id=user_id)
    #         return addresses

    # async def update_address(self, address: AddressUpdateDTO, user_id: UUID, address_id: UUID) -> Address:
    #     """
    #     Обновляет адрес.
    #     :param address: Адрес для обновления.
    #     :return: Обновленный адрес.
    #     """

    #     async with self._uow as uow:
    #         current_address = await uow.address_repository.get_address(address_id=address_id)
    #         if current_address is None:
    #             logger.warning("Адрес с id=%s не найден", address_id)
    #             raise AddressNotFoundError("Адрес не найден")
    #         if current_address.user_id != user_id:
    #             logger.warning("Адрес с id=%s не принадлежит пользователю с id=%s", address_id, user_id)
    #             raise ForbiddenError("Адрес не принадлежит пользователю")
    #         updated_address = await uow.address_repository.update(address=address, address_id=address_id)
    #         if updated_address is None:
    #             logger.warning("Адрес с id=%s не найден", address_id)
    #             raise AddressNotFoundError("Адрес не найден")
    #         return updated_address

    # async def delete_address(self, address_id: UUID, user_id: UUID) -> Address:
    #     """
    #     Удаляет адрес.
    #     :param address_id: ID адреса.
    #     :return: Удаленный адрес.
    #     """

    #     async with self._uow as uow:
    #         current_address = await uow.address_repository.get_address(address_id=address_id)
    #         if current_address is None:
    #             logger.warning("Адрес с id=%s не найден", address_id)
    #             raise AddressNotFoundError("Адрес не найден")
    #         if current_address.user_id != user_id:
    #             logger.warning("Адрес с id=%s не принадлежит пользователю с id=%s", address_id, user_id)
    #             raise ForbiddenError("Адрес не принадлежит пользователю")
    #         deleted_address = await uow.address_repository.delete(address_id=address_id)
    #         if deleted_address is None:
    #             logger.warning("Адрес с id=%s не найден", address_id)
    #             raise AddressNotFoundError("Адрес не найден")
    #         return deleted_address
