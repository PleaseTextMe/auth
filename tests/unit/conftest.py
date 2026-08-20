from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_result():
    """Generic mock for database query results."""
    return MagicMock()


@pytest.fixture
def mock_query():
    """Generic mock for database queries."""
    return MagicMock()


@pytest.fixture
def mock_session(mock_result):
    """Mock database session that returns the generic mock_result by default."""
    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = mock_result
    return session


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    # Use simple AsyncMock to ensure methods are awaitable,
    # as spec=Redis breaks introspection of dynamically generated async methods.
    return AsyncMock()


@pytest.fixture
def mock_db_model():
    """Generic mock for SQLAlchemy database models."""
    return MagicMock()


@pytest.fixture
def mock_domain_model():
    """Generic mock for domain entities/models."""
    return MagicMock()


@pytest.fixture
def mock_uow():
    """Mock for Unit of Work."""
    uow = AsyncMock()
    uow.user_repository = AsyncMock()
    uow.verify_repository = AsyncMock()
    uow.session_repository = AsyncMock()
    # Support async context manager
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow
