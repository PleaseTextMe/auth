from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_redis():
    return AsyncMock(spec=Redis)


@pytest.fixture
def mock_db_user():
    return MagicMock()


@pytest.fixture
def mock_user_instance():
    return MagicMock(spec=User)


@pytest.fixture
def mock_select():
    with patch("src.infrastructure.repositories.user.select") as mock:
        yield mock


@pytest.fixture
def mock_insert():
    with patch("src.infrastructure.repositories.user.insert") as mock:
        yield mock


@pytest.fixture
def mock_model_validate():
    with patch("src.infrastructure.repositories.user.User.model_validate") as mock:
        yield mock
