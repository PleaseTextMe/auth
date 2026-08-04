import logging
from datetime import timedelta

from redis.asyncio import Redis

from src.services.interfaces.repositories.blacklist import IBlacklistRepository

logger = logging.getLogger(__name__)


class RedisBlacklistRepository(IBlacklistRepository):
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def get_value(self, key: str) -> str | None:
        value = await self._client.get(key)
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else value

    async def set_value(self, key: str, value: str, exp: timedelta | None = None) -> None:
        await self._client.set(key, value, ex=exp)

    async def set_many_values(self, values: dict[str, str], exp: timedelta | None = None) -> None:
        async with self._client.pipeline(transaction=True) as pipe:
            for key, value in values.items():
                pipe.set(key, value, ex=exp)
            await pipe.execute()
