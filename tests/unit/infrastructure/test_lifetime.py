from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.config import PostgresSettings, settings
from src.infrastructure import lifetime as lifetime_module
from src.infrastructure.db import postgres, redis
from src.infrastructure.lifetime import AppLifetime


@pytest.fixture
def runtime(monkeypatch):
    monkeypatch.setattr(postgres, "engine", None)
    monkeypatch.setattr(postgres, "session_maker", None)
    monkeypatch.setattr(redis, "redis_client", None)
    monkeypatch.setattr(
        settings, "postgres",
        PostgresSettings(
            _env_file=None, POSTGRES_HOST="127.0.0.1", POSTGRES_PORT=5435,
            POSTGRES_DB="lifetime_test", POSTGRES_USER="test_user",
            POSTGRES_PASSWORD="test:p@ss/%#word",
        ),
    )
    monkeypatch.setattr(lifetime_module, "start_mappers", MagicMock())
    monkeypatch.setattr(lifetime_module, "clear_mappers", MagicMock())
    return AppLifetime()


@pytest.mark.asyncio
async def test_startup_uses_complete_database_url_and_can_restart(runtime):
    # Keep the real engine constructor: mocking it would hide invalid URL errors.
    with patch.object(AsyncEngine, "begin") as begin, patch.object(
        lifetime_module.Redis, "from_url", return_value=AsyncMock()
    ) as redis_factory:
        begin.return_value.__aenter__ = AsyncMock()
        begin.return_value.__aexit__ = AsyncMock()
        for _ in range(2):
            await runtime.startup()
            try:
                url = postgres.engine.url
                assert url.drivername == "postgresql+asyncpg"
                assert url.host == "127.0.0.1"
                assert url.port == 5435
                assert url.database == "lifetime_test"
                assert url.username == "test_user"
                assert url.password == "test:p@ss/%#word"
                assert postgres.session_maker is not None
            finally:
                await runtime.shutdown()
            assert postgres.engine is None
            assert postgres.session_maker is None
            assert redis.redis_client is None
        assert redis_factory.return_value.aclose.await_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("failed_service", ["postgres", "redis"])
async def test_failed_startup_closes_initialized_resources(runtime, failed_service):
    client = AsyncMock()
    with patch.object(AsyncEngine, "begin") as begin, patch.object(
        AsyncEngine, "dispose", new_callable=AsyncMock
    ) as dispose, patch.object(lifetime_module.Redis, "from_url", return_value=client):
        begin.return_value.__aenter__ = AsyncMock()
        begin.return_value.__aexit__ = AsyncMock()
        if failed_service == "postgres":
            begin.return_value.__aenter__.side_effect = RuntimeError("database unavailable")
        else:
            client.ping.side_effect = RuntimeError("redis unavailable")
        with pytest.raises(RuntimeError, match="unavailable"):
            await runtime.startup()

        dispose.assert_awaited_once()
        if failed_service == "redis":
            client.aclose.assert_awaited_once()
        else:
            client.aclose.assert_not_awaited()
        assert postgres.engine is None
        assert postgres.session_maker is None
        assert redis.redis_client is None
        lifetime_module.clear_mappers.assert_called_once()


@pytest.mark.asyncio
async def test_shutdown_cleans_redis_even_when_postgres_disposal_fails(runtime):
    postgres.engine = AsyncMock()
    postgres.engine.dispose.side_effect = RuntimeError("dispose failed")
    postgres.session_maker = MagicMock()
    client = AsyncMock()
    redis.redis_client = client

    with pytest.raises(RuntimeError, match="dispose failed"):
        await runtime.shutdown()

    client.aclose.assert_awaited_once()
    assert postgres.engine is None
    assert postgres.session_maker is None
    assert redis.redis_client is None
    lifetime_module.clear_mappers.assert_called_once()

