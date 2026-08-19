from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.session import SQLAlchemySessionRepository
from src.infrastructure.repositories.user import SQLAlchemyUserRepository
from src.infrastructure.repositories.verify import RedisVerifyRepository
from src.services.interfaces.repositories.session import ISessionRepository
from src.services.interfaces.repositories.user import IUserRepository
from src.services.interfaces.repositories.verify import IVerifyRepository
from src.services.interfaces.uow import IUnitOfWork

# from src.services.interfaces.producer import IProducer


class DatabaseUnitOfWork(IUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis,
        # producer: IProducer
    ):
        self.session = session
        self.redis = redis
        # self._producer = producer

    async def __aenter__(self) -> "DatabaseUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
        if self.session.is_active:
            await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    # @property
    # def producer(self) -> IProducer:
    #     return self._producer

    @property
    def user_repository(self) -> IUserRepository:
        return SQLAlchemyUserRepository(self.session)

    @property
    def session_repository(self) -> ISessionRepository:
        return SQLAlchemySessionRepository(self.session)

    @property
    def verify_repository(self) -> IVerifyRepository:
        return RedisVerifyRepository(self.redis)
