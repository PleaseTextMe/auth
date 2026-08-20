from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.entities.session import Session
from src.domain.entities.user import User
from src.services.session import ISessionService
from src.services.user import IUserService
from src.services.verify import IVerifyService


@pytest.fixture
def mock_user_service():
    """Mock for IUserService."""
    return AsyncMock(spec=IUserService)


@pytest.fixture
def mock_session_service():
    """Mock for ISessionService with default create return value."""
    service = AsyncMock(spec=ISessionService)
    service.create.return_value = "mock_auth_token"
    return service


@pytest.fixture
def mock_verify_service():
    """Mock for IVerifyService with default create_email_code return value."""
    service = AsyncMock(spec=IVerifyService)
    service.create_email_code.return_value = "mock_verify_token"
    return service


@pytest.fixture
def valid_session():
    """A valid domain Session entity for testing."""
    return Session(
        id=1,
        user_id=1,
        auth_token_hash=b"hash",
        user_agent="agent",
        user_ip="ip",
        device_type="web",
        is_active=True,
    )


@pytest.fixture
def valid_user():
    """A valid domain User entity for testing."""
    return User(
        id=1,
        email="axel@harlem.hui",
        username="testuser",
        password_hash="hash",
        public_bundle={"key": "val"},
        vault={"key": "val"},
        is_active=True,
    )


@pytest.fixture
async def test_client(test_app):
    """Async HTTP client connected to the test app via ASGITransport."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac
