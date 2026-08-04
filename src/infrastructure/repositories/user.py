import logging
from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import Result, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

# from src.domain.dtos.address import AddressCreateDTO, AddressUpdateDTO
from src.domain.entities.user import User, UserSalt
# from src.infrastructure.repositories.exceptions import NotModifiedError
from src.services.interfaces.repositories.user import IUserRepository

logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    # async def create(self, address: AddressCreateDTO) -> Address:
    #     insert_data = address.model_dump()
    #     insert_data["location"] = WKTElement(
    #         f"POINT({address.longitude} {address.latitude})", srid=4326
    #     )
    #     query = insert(Address).values(insert_data).returning(Address)
    #     result: Result = await self._session.execute(query)
    #     return result.unique().scalar_one()

    # async def get_address(self, address_id: UUID) -> Address | None:
    #     query = select(Address).filter_by(id=address_id)
    #     result: Result = await self._session.execute(query)
    #     address = result.scalar_one_or_none()
    #     if address is None:
    #         logger.warning("Address с id=%s не найден.", address_id)
    #         return None
    #     return address

    async def get_salt(self, user_email: str) -> UserSalt | None:
        query = select(User).filter_by(email=user_email)
        result: Result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        return UserSalt.model_validate(user) if user else None

    # async def delete(self, address_id: UUID) -> Address | None:
    #     query = select(Address).filter_by(id=address_id)
    #     result: Result = await self._session.execute(query)
    #     address = result.scalar_one_or_none()
    #     if address is None:
    #         logger.warning("Удаляемый Address с id=%s не найден.", address_id)
    #         return None

    #     await self._session.delete(address)
    #     return address

    # async def update(
    #     self, address: AddressUpdateDTO, address_id: UUID
    # ) -> Address | None:
    #     update_data = address.model_dump(
    #         exclude_unset=True, exclude_defaults=True, exclude={"id"}
    #     )
    #     if not update_data:
    #         raise NotModifiedError("Не указаны данные для обновления.")
    #     if update_data.get("latitude") and update_data.get("longitude"):
    #         update_data["location"] = WKTElement(
    #             f"POINT({update_data['longitude']} {update_data['latitude']})",
    #             srid=4326,
    #         )

    #     query = update(Address).where(Address.id == address_id).values(**update_data).returning(Address)  # type: ignore
    #     result: Result = await self._session.execute(query)
    #     updated_address = result.scalar_one_or_none()
    #     if updated_address is None:
    #         logger.warning("Address с id=%s не найден для обновления.", address_id)
    #         return None
    #     return updated_address

    # async def get_nearby_addresses(
    #     self, latitude: float, longitude: float, radius: float = 3
    # ) -> Iterable[Address]:
    #     """
    #     Получает список адресов в зависимости от радиуса от заданной точки.
    #     :param latitude: Широта
    #     :param longitude: Долгота
    #     :param radius: Радиус в метрах
    #     :return: Список адресов
    #     """

    #     query = select(Address).where(
    #         Address.location.ST_DWithin(
    #             WKTElement(f"POINT({longitude} {latitude})", srid=4326), radius * 1000
    #         )
    #     )
    #     result: Result = await self._session.execute(query)
    #     return result.unique().scalars().all()