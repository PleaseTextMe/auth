from collections.abc import AsyncIterable
from datetime import timedelta

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.infrastructure.db import postgres

# from src.infrastructure.messaging import producer
from src.infrastructure.uow import SQLAlchemyUnitOfWork
from src.services.blacklist import BlacklistService, IBlacklistService
from src.services.interfaces.uow import IUnitOfWork
from src.services.jwt import IJWTService, JWTService
from src.services.user import IUserService, UserService


class Container(Provider):
    # @provide(scope=Scope.APP)
    # async def provide_rabbitmq_producer(self) -> IProducer:
    #     if producer.producer is None:
    #         raise RuntimeError("RabbitMQ producer is not initialized")
    #     return producer.producer

    @provide(scope=Scope.REQUEST)
    async def provide_session(self) -> AsyncIterable[AsyncSession]:
        if postgres.session_maker is None:
            raise RuntimeError("Session maker is not initialized")
        async with postgres.session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    # async def provide_uow(self, session: AsyncSession, producer: IProducer) -> IUnitOfWork:
    async def provide_uow(self, session: AsyncSession) -> IUnitOfWork:
        return SQLAlchemyUnitOfWork(session)

    @provide(scope=Scope.REQUEST)
    async def provide_blacklist_service(self, uow: IUnitOfWork) -> IBlacklistService:
        return BlacklistService(uow)

    @provide(scope=Scope.REQUEST)
    async def provide_jwt_service(self) -> IJWTService:
        return JWTService(
            secret_key=settings.service.secret_key.get_secret_value(),
            algorithm=settings.service.jwt_algorithm,
            access_token_lifetime=timedelta(minutes=30),
            refresh_token_lifetime=timedelta(days=30),
        )

    @provide(scope=Scope.REQUEST)
    async def provide_user_service(self, uow: IUnitOfWork) -> IUserService:
        return UserService(uow)
