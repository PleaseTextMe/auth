from abc import ABC, abstractmethod

# from src.services.interfaces.producer import IProducer

from src.services.interfaces.repositories.blacklist import IBlacklistRepository
from src.services.interfaces.repositories.user import IUserRepository
# from src.services.interfaces.repositories.event import IEventRepository
# from src.services.interfaces.repositories.subscription import ISubscriptionRepository
# from src.services.interfaces.repositories.feedback import IFeedbackRepository
# from src.services.interfaces.repositories.reservation import IReservationRepository


class IUnitOfWork(ABC):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...

    # @property
    # @abstractmethod
    # def producer(self) -> IProducer: ...

    # @property
    # @abstractmethod
    # def subscription_repository(self) -> ISubscriptionRepository: ...

    # @property
    # @abstractmethod
    # def event_repository(self) -> IEventRepository: ...

    @property
    @abstractmethod
    def blacklist_repository(self) -> IBlacklistRepository: ...

    @property
    @abstractmethod
    def user_repository(self) -> IUserRepository: ...

    # @property
    # @abstractmethod
    # def reservation_repository(self) -> IReservationRepository: ...

    # @property
    # @abstractmethod
    # def event_feedback_repository(self) -> IFeedbackRepository: ...

    # @property
    # @abstractmethod
    # def user_feedback_repository(self) -> IFeedbackRepository: ...
