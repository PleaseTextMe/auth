from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

engine: AsyncEngine | None = None
session_maker: async_sessionmaker[AsyncSession] | None = None


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if session_maker is None:
        raise RuntimeError("Session maker is not initialized")

    async with session_maker() as session:
        yield session
