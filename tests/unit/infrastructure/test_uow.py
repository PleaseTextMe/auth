from unittest.mock import AsyncMock

import pytest
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.session import SQLAlchemySessionRepository
from src.infrastructure.repositories.user import SQLAlchemyUserRepository
from src.infrastructure.repositories.verify import RedisVerifyRepository
from src.infrastructure.uow import DatabaseUnitOfWork


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_redis():
    return AsyncMock(spec=Redis)


@pytest.fixture
def uow(mock_session, mock_redis):
    return DatabaseUnitOfWork(session=mock_session, redis=mock_redis)


@pytest.mark.asyncio
async def test_uow_aenter(uow):
    result = await uow.__aenter__()
    assert result is uow


@pytest.mark.asyncio
async def test_uow_aexit_no_exception(uow, mock_session):
    mock_session.is_active = True
    await uow.__aexit__(None, None, None)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()
    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_uow_aexit_with_exception(uow, mock_session):
    mock_session.is_active = True
    await uow.__aexit__(Exception, Exception("error"), None)
    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_uow_aexit_not_active(uow, mock_session):
    mock_session.is_active = False
    await uow.__aexit__(None, None, None)
    mock_session.commit.assert_called_once()
    mock_session.close.assert_not_called()


@pytest.mark.asyncio
async def test_uow_commit(uow, mock_session):
    await uow.commit()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_uow_rollback(uow, mock_session):
    await uow.rollback()
    mock_session.rollback.assert_called_once()


def test_uow_user_repository(uow):
    repo = uow.user_repository
    assert isinstance(repo, SQLAlchemyUserRepository)
    assert repo._session is uow.session


def test_uow_session_repository(uow):
    repo = uow.session_repository
    assert isinstance(repo, SQLAlchemySessionRepository)
    assert repo._session is uow.session


def test_uow_verify_repository(uow):
    repo = uow.verify_repository
    assert isinstance(repo, RedisVerifyRepository)
    assert repo._redis is uow.redis
