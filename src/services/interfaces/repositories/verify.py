import abc
from datetime import timedelta
from typing import Any


class IVerifyRepository(abc.ABC):

    @abc.abstractmethod
    async def get_value(self, key: str) -> str | None: ...

    @abc.abstractmethod
    async def set_value(
        self,
        key: str,
        value: str,
        exp: timedelta | int | None = None
    ) -> None: ...

    @abc.abstractmethod
    async def delete_value(self, key: str) -> None: ...

    @abc.abstractmethod
    async def update_field(
        self,
        key: str,
        field: str,
        value: Any,
        new_exp: timedelta | int | None = None
    ) -> None: ...
