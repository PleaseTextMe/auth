from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db import redis
from src.infrastructure.repositories.blacklist import RedisBlacklistRepository

# from src.services.interfaces.repositories.feedback import IFeedbackRepository
from src.infrastructure.repositories.user import SQLAlchemyUserRepository
from src.services.interfaces.repositories.blacklist import IBlacklistRepository
from src.services.interfaces.repositories.user import IUserRepository

# from src.infrastructure.repositories.events import SQLAlchemyEventRepository
# from src.infrastructure.repositories.reservations import SQLAlchemyReservationRepository
# from src.infrastructure.repositories.subscriptions import (
#     SQLAlchemySubscriptionRepository,
# )
# from src.services.interfaces.producer import IProducer
# from src.services.interfaces.repositories.event import IEventRepository
# from src.services.interfaces.repositories.reservation import IReservationRepository
# from src.services.interfaces.repositories.subscription import ISubscriptionRepository
from src.services.interfaces.uow import IUnitOfWork

# from src.infrastructure.repositories.event_feedbacks import (
#     SQLAlchemyEventFeedbackRepository,
#     IEventFeedbackRepository,
# )
# from src.infrastructure.repositories.user_feedbacks import (
#     SQLAlchemyUserFeedbackRepository,
# )


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(
            self,
            session: AsyncSession,
            # producer: IProducer
        ):
        self.session = session
        # self._producer = producer

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
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


    # @property
    # def subscription_repository(self) -> ISubscriptionRepository:
    #     return SQLAlchemySubscriptionRepository(self.session)

    # @property
    # def event_repository(self) -> IEventRepository:
    #     return SQLAlchemyEventRepository(self.session)

    # @property
    # def reservation_repository(self) -> IReservationRepository:
    #     return SQLAlchemyReservationRepository(self.session)

    @property
    def user_repository(self) -> IUserRepository:
        return SQLAlchemyUserRepository(self.session)

    @property
    def blacklist_repository(self) -> IBlacklistRepository:
        if redis.client is None:
            raise RuntimeError("Redis is not initialized")
        return RedisBlacklistRepository(redis.client)

    # @property
    # def event_feedback_repository(self) -> IEventFeedbackRepository:
    #     return SQLAlchemyEventFeedbackRepository(self.session)

    # @property
    # def user_feedback_repository(self) -> IFeedbackRepository:
    #     return SQLAlchemyUserFeedbackRepository(self.session)
