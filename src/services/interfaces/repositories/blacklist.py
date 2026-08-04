import abc
from datetime import timedelta


class IBlacklistRepository(abc.ABC):

    @abc.abstractmethod
    async def get_value(self, key: str) -> str | None: ...

    @abc.abstractmethod
    async def set_value(self, key: str, value: str, exp: timedelta | None = None) -> None: ...

    @abc.abstractmethod
    async def set_many_values(self, values: dict[str, str], exp: timedelta | None = None) -> None: ...
