from unittest.mock import AsyncMock, patch

import pytest

from src.infrastructure.container import Container
from src.infrastructure.db import postgres
from src.infrastructure.db.postgres import get_session
from src.infrastructure.lifetime import AppLifetime


@pytest.mark.asyncio
async def test_get_session_uninitialized():
    postgres.session_maker = None
    with pytest.raises(RuntimeError, match="Session maker is not initialized"):
        async with get_session():
            pass


@pytest.mark.asyncio
async def test_container_provide_session_uninitialized():
    postgres.session_maker = None
    container = Container()
    with pytest.raises(RuntimeError, match="Session maker is not initialized"):
        async for _ in container.provide_session():
            pass


@pytest.mark.asyncio
async def test_app_lifetime_postgres_error():
    lifetime = AppLifetime()
    with patch("src.infrastructure.lifetime.create_async_engine") as mock_engine:
        mock_engine.return_value.begin.side_effect = Exception("DB Connection Error")
        with pytest.raises(Exception, match="DB Connection Error"):
            await lifetime.startup()


@pytest.mark.asyncio
async def test_app_lifetime_redis_error():
    lifetime = AppLifetime()
    with patch("src.infrastructure.lifetime.create_async_engine") as mock_engine, patch("src.infrastructure.lifetime.Redis.from_url") as mock_redis:
        mock_engine.return_value.begin.return_value.__aenter__ = AsyncMock()
        mock_engine.return_value.begin.return_value.__aexit__ = AsyncMock()
        mock_redis.return_value.ping.side_effect = Exception("Redis Connection Error")
        with pytest.raises(Exception, match="Redis Connection Error"):
            await lifetime.startup()
