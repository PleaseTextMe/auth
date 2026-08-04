from abc import ABC, abstractmethod


class AbstractAppLifetime(ABC):
    @abstractmethod
    async def startup(self) -> None: ...

    @abstractmethod
    async def shutdown(self) -> None: ...
