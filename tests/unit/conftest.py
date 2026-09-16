from unittest.mock import AsyncMock, MagicMock

import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.router import router
from src.api.v1.depends import get_current_session, get_current_user
from src.domain.entities.session import Session
from src.domain.entities.user import User
from src.services.interfaces.uow import IUnitOfWork
from src.services.session import ISessionService
from src.services.user import IUserService
from src.services.verify import IVerifyService


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
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def mock_request():
    """Mock FastAPI Request object."""
    return AsyncMock(spec=Request)


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
async def test_app(
    mock_user_service, mock_session_service, mock_verify_service, mock_uow, valid_session, valid_user
):
    """Universal FastAPI test application with configured Dishka container and dependency overrides."""
    app = FastAPI()
    app.include_router(router)

    class MockProvider(Provider):
        @provide(scope=Scope.APP)
        def get_user_service(self) -> IUserService:
            return mock_user_service

        @provide(scope=Scope.APP)
        def get_session_service(self) -> ISessionService:
            return mock_session_service

        @provide(scope=Scope.APP)
        def get_verify_service(self) -> IVerifyService:
            return mock_verify_service

        @provide(scope=Scope.APP)
        def get_uow(self) -> IUnitOfWork:
            return mock_uow

    container = make_async_container(MockProvider())
    setup_dishka(container=container, app=app)

    app.dependency_overrides[get_current_session] = lambda: valid_session
    app.dependency_overrides[get_current_user] = lambda: valid_user

    yield app
    await container.close()


@pytest.fixture
async def test_client(test_app):
    """Async HTTP client connected to the test app via ASGITransport."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac
