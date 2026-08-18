import json
from datetime import timedelta
from unittest.mock import AsyncMock

import pytest

from src.infrastructure.repositories.verify import RedisVerifyRepository


@pytest.fixture
def mock_redis():
    # Use simple AsyncMock to ensure methods are awaitable
    return AsyncMock()


@pytest.fixture
def repo(mock_redis):
    return RedisVerifyRepository(redis=mock_redis)


def test_make_key(repo):
    assert repo._make_key("test") == "verify:test"


@pytest.mark.asyncio
async def test_get_value_found(repo, mock_redis):
    mock_redis.get.return_value = b"test_value"
    result = await repo.get_value("test")
    assert result == "test_value"
    mock_redis.get.assert_called_once_with(name="verify:test")


@pytest.mark.asyncio
async def test_get_value_not_found(repo, mock_redis):
    mock_redis.get.return_value = None
    result = await repo.get_value("test")
    assert result is None
    mock_redis.get.assert_called_once_with(name="verify:test")


@pytest.mark.asyncio
async def test_set_value_no_exp(repo, mock_redis):
    await repo.set_value("test", "value")
    mock_redis.set.assert_called_once_with(name="verify:test", value="value")


@pytest.mark.asyncio
async def test_set_value_with_exp_int(repo, mock_redis):
    await repo.set_value("test", "value", exp=5)
    mock_redis.set.assert_called_once_with(name="verify:test", value="value", ex=300)


@pytest.mark.asyncio
async def test_set_value_with_exp_timedelta(repo, mock_redis):
    await repo.set_value("test", "value", exp=timedelta(minutes=10))
    mock_redis.set.assert_called_once_with(name="verify:test", value="value", ex=600)


@pytest.mark.asyncio
async def test_delete_value(repo, mock_redis):
    await repo.delete_value("test")
    mock_redis.delete.assert_called_once_with("verify:test")


@pytest.mark.asyncio
async def test_update_field_no_data(repo, mock_redis):
    mock_redis.get.return_value = None
    await repo.update_field("test", "field", "value")
    mock_redis.get.assert_called_once_with("verify:test")
    mock_redis.set.assert_not_called()


@pytest.mark.asyncio
async def test_update_field_with_data_no_new_exp_has_ttl(repo, mock_redis):
    mock_redis.get.return_value = json.dumps({"old_field": "old"}).encode("utf-8")
    mock_redis.ttl.return_value = 100

    await repo.update_field("test", "field", "value")

    expected_data = json.dumps({"old_field": "old", "field": "value"})
    mock_redis.set.assert_called_once_with("verify:test", expected_data, ex=100)


@pytest.mark.asyncio
async def test_update_field_with_data_no_new_exp_no_ttl(repo, mock_redis):
    mock_redis.get.return_value = json.dumps({"old_field": "old"}).encode("utf-8")
    mock_redis.ttl.return_value = -1

    await repo.update_field("test", "field", "value")

    expected_data = json.dumps({"old_field": "old", "field": "value"})
    mock_redis.set.assert_called_once_with("verify:test", expected_data)


@pytest.mark.asyncio
async def test_update_field_with_new_exp_int(repo, mock_redis):
    mock_redis.get.return_value = json.dumps({"old_field": "old"}).encode("utf-8")

    await repo.update_field("test", "field", "value", new_exp=5)

    expected_data = json.dumps({"old_field": "old", "field": "value"})
    mock_redis.set.assert_called_once_with("verify:test", expected_data, ex=300)


@pytest.mark.asyncio
async def test_update_field_with_new_exp_timedelta(repo, mock_redis):
    mock_redis.get.return_value = json.dumps({"old_field": "old"}).encode("utf-8")

    await repo.update_field("test", "field", "value", new_exp=timedelta(minutes=10))

    expected_data = json.dumps({"old_field": "old", "field": "value"})
    mock_redis.set.assert_called_once_with("verify:test", expected_data, ex=600)
