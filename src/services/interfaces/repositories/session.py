import abc

from src.domain.entities.session import Session


class ISessionRepository(abc.ABC):
    @abc.abstractmethod
    async def create(self, session_data: Session) -> Session: ...

    @abc.abstractmethod
    async def get_by_hash(self, auth_token_hash: bytes) -> Session: ...

    @abc.abstractmethod
    async def deactivate_token(self, auth_token_hash: bytes): ...
