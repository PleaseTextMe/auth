from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.infrastructure.db import postgres
from src.infrastructure.uow import DatabaseUnitOfWork
from src.services.interfaces.uow import IUnitOfWork
from src.services.session import ISessionService, SessionService
from src.services.user import IUserService, UserService
from src.services.verify import IVerifyService, VerifyService

# from src.infrastructure.messaging import producer


class Container(Provider):
    # @provide(scope=Scope.APP)
    # async def provide_rabbitmq_producer(self) -> IProducer:
    #     if producer.producer is None:
    #         raise RuntimeError("RabbitMQ producer is not initialized")
    #     return producer.producer

    @provide(scope=Scope.APP)
    async def provide_redis(self) -> AsyncIterable[Redis]:
        client = Redis.from_url(settings.redis.url)
        yield client
        await client.aclose()

    @provide(scope=Scope.REQUEST)
    async def provide_session(self) -> AsyncIterable[AsyncSession]:
        if postgres.session_maker is None:
            raise RuntimeError("Session maker is not initialized")
        async with postgres.session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    # async def provide_uow(self, session: AsyncSession, producer: IProducer) -> IUnitOfWork:
    async def provide_uow(self, session: AsyncSession, redis: Redis) -> IUnitOfWork:
        return DatabaseUnitOfWork(session, redis)

    @provide(scope=Scope.REQUEST)
    async def provide_session_service(self, uow: IUnitOfWork) -> ISessionService:
        return SessionService(uow)

    @provide(scope=Scope.REQUEST)
    async def provide_user_service(self, uow: IUnitOfWork) -> IUserService:
        return UserService(uow)

    @provide(scope=Scope.REQUEST)
    async def provide_verify_service(self, uow: IUnitOfWork) -> IVerifyService:
        return VerifyService(uow)
