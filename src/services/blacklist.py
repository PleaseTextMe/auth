from abc import ABC, abstractmethod
from datetime import timedelta

from src.services.interfaces.uow import IUnitOfWork


class IBlacklistService(ABC):

    @abstractmethod
    async def is_exists(self, key: str) -> bool: ...

    @abstractmethod
    async def set_one_value(self, key: str, value: str, exp: timedelta | None = None): ...

    @abstractmethod
    async def set_many_values(self, values: dict[str, str], exp: timedelta | None = None): ...


class BlacklistService(IBlacklistService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def is_exists(self, key: str) -> bool:
        """
        Проверяет, существует ли ключ в черном списке.
        :param key: Ключ (например, идентификатор токена).
        :return: True, если ключ существует, иначе False.
        """
        async with self._uow as uow:
            value = await uow.blacklist_repository.get_value(key=key)
            return value is not None

    async def set_one_value(self, key: str, value: str, exp: timedelta | None = None):
        """
        Добавляет один ключ в черный список.
        :param key: Ключ (например, идентификатор токена).
        :param value: Значение, связанное с ключом.
        :param exp: Время жизни ключа (если не указано, ключ будет без срока действия).
        """
        async with self._uow as uow:
            await uow.blacklist_repository.set_value(
                key=str(key),
                value=str(value),
                exp=exp
            )

    async def set_many_values(self, values: dict[str, str], exp: timedelta | None = None):
        """
        Добавляет несколько значений в храниРепозиторий для управления данными слище.
        :param values: Словарь {ключ: значение}.
        :param exp: Время жизни ключей (если указано, будет установлено время истечения).
        """
        async with self._uow as uow:
            values = {str(k): str(v) for k, v in values.items()}
            await uow.blacklist_repository.set_many_values(values=values, exp=exp)
