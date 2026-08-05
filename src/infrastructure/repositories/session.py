import logging

from sqlalchemy import Result, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.session import Session
from src.services.interfaces.repositories.session import ISessionRepository

logger = logging.getLogger(__name__)


class SQLAlchemySessionRepository(ISessionRepository):
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    async def create(self, session_data: Session) -> Session:
        insert_data = session_data.model_dump()
        insert_data["auth_token_hash"] = session_data.auth_token_hash
        query = insert(Session).values(insert_data).returning(Session)
        result: Result = await self._session.execute(query)
        db_session = result.unique().scalar_one()
        return Session.model_validate(db_session)

    async def get_by_hash(self, auth_token_hash: bytes) -> Session:
        query = select(Session).filter_by(auth_token_hash=auth_token_hash)
        result: Result = await self._session.execute(query)
        db_session = result.scalar_one_or_none()
        return Session.model_validate(db_session) if db_session else None

    async def deactivate_token(self, auth_token_hash: bytes):
        query = (
            update(Session)
            .where(Session.auth_token_hash == auth_token_hash)
            .values(is_active=False)
        )
        await self._session.execute(query)
