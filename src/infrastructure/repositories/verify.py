import json
from datetime import timedelta
from typing import Any

from redis.asyncio import Redis

from src.services.interfaces.repositories.verify import IVerifyRepository


class RedisVerifyRepository(IVerifyRepository):
    # Префикс гарантирует, что ключи верификации никогда не пересекутся с сессиями
    PREFIX = "verify:"

    def __init__(self, redis: Redis):
        self._redis = redis

    def _make_key(self, key: str) -> str:
        return f"{self.PREFIX}{key}"

    async def get_value(self, key: str) -> str | None:
        value = await self._redis.get(name=self._make_key(key))
        return value.decode("utf-8") if value else None

    async def set_value(self, key: str, value: str, exp: timedelta | int | None = None) -> None:
        if exp is not None:
            if isinstance(exp, int):
                exp_seconds = int(timedelta(minutes=exp).total_seconds())
            else:
                exp_seconds = int(exp.total_seconds())
                
            await self._redis.set(name=self._make_key(key), value=value, ex=exp_seconds)
        else:
            await self._redis.set(name=self._make_key(key), value=value)

    async def delete_value(self, key: str) -> None:
        await self._redis.delete(self._make_key(key))

    async def update_field(
        self, 
        key: str, 
        field: str, 
        value: Any, 
        new_exp: timedelta | int | None = None
    ) -> None:
        full_key = self._make_key(key)
        raw_data = await self._redis.get(full_key)
        
        if not raw_data:
            return  

        data = json.loads(raw_data.decode("utf-8"))
        data[field] = value
        
        if new_exp is not None:
            if isinstance(new_exp, int):
                ttl = int(timedelta(minutes=new_exp).total_seconds())
            else:
                ttl = int(new_exp.total_seconds())
        else:
            ttl = await self._redis.ttl(full_key)
        
        if ttl > 0:
            await self._redis.set(full_key, json.dumps(data), ex=ttl)
        else: 
            await self._redis.set(full_key, json.dumps(data))
