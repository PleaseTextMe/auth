import json

import pytest
from redis.asyncio import Redis

from src.core.config import settings
from src.infrastructure.repositories.verify import RedisVerifyRepository


@pytest.fixture
async def redis_client():
    client = Redis.from_url(settings.redis.url)
    yield client
    await client.aclose()


@pytest.fixture
def repo(redis_client):
    return RedisVerifyRepository(redis=redis_client)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_verify_repository_set_and_get(repo: RedisVerifyRepository):
    key = "venya_key_1"
    value = "HelloToPavelDurov"

    await repo.set_value(key, value)

    fetched = await repo.get_value(key)
    assert fetched == value

    await repo.delete_value(key)
    fetched_after = await repo.get_value(key)
    assert fetched_after is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_verify_repository_update_field(repo: RedisVerifyRepository):

    key = "animan_json"
    initial_value = {"email": "axel@harlem.hui", "verified": False}

    await repo.set_value(key, json.dumps(initial_value))

    await repo.update_field(key, "verified", True)

    fetched = await repo.get_value(key)
    assert fetched is not None

    data = json.loads(fetched)
    assert data["verified"] is True
    assert data["email"] == "axel@harlem.hui"
