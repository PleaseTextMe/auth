import json
from datetime import timedelta

import pytest

from src.infrastructure.repositories.verify import RedisVerifyRepository


@pytest.fixture
def repo(mock_redis):
    return RedisVerifyRepository(redis=mock_redis)


def test_make_key(repo):
    assert repo._make_key("Venya") == "verify:Venya"


@pytest.mark.asyncio
async def test_get_value_found(repo, mock_redis):
    mock_redis.get.return_value = b"test_value"
    result = await repo.get_value("Venya")
    assert result == "test_value"
    mock_redis.get.assert_called_once_with(name="verify:Venya")


@pytest.mark.asyncio
async def test_get_value_not_found(repo, mock_redis):
    mock_redis.get.return_value = None
    result = await repo.get_value("Venya")
    assert result is None
    mock_redis.get.assert_called_once_with(name="verify:Venya")


@pytest.mark.asyncio
async def test_set_value_no_exp(repo, mock_redis):
    await repo.set_value("Venya", "value")
    mock_redis.set.assert_called_once_with(name="verify:Venya", value="value")


@pytest.mark.asyncio
async def test_set_value_with_exp_int(repo, mock_redis):
    await repo.set_value("Venya", "value", exp=5)
    mock_redis.set.assert_called_once_with(name="verify:Venya", value="value", ex=300)


@pytest.mark.asyncio
async def test_set_value_with_exp_timedelta(repo, mock_redis):
    await repo.set_value("Venya", "value", exp=timedelta(minutes=10))
    mock_redis.set.assert_called_once_with(name="verify:Venya", value="value", ex=600)


@pytest.mark.asyncio
async def test_delete_value(repo, mock_redis):
    await repo.delete_value("Venya")
    mock_redis.delete.assert_called_once_with("verify:Venya")


@pytest.mark.asyncio
async def test_update_field_no_data(repo, mock_redis):
    mock_redis.get.return_value = None
    await repo.update_field("Venya", "field", "value")
    mock_redis.get.assert_called_once_with("verify:Venya")
    mock_redis.set.assert_not_called()


@pytest.mark.asyncio
async def test_update_field_with_data_no_new_exp_has_ttl(repo, mock_redis):
    mock_redis.get.return_value = json.dumps({"old_field": "old"}).encode("utf-8")
    mock_redis.ttl.return_value = 100

    await repo.update_field("Venya", "field", "value")

    expected_data = json.dumps({"old_field": "old", "field": "value"})
    mock_redis.set.assert_called_once_with("verify:Venya", expected_data, ex=100)


@pytest.mark.asyncio
async def test_update_field_with_data_no_new_exp_no_ttl(repo, mock_redis):
    mock_redis.get.return_value = json.dumps({"old_field": "old"}).encode("utf-8")
    mock_redis.ttl.return_value = -1

    await repo.update_field("Venya", "field", "value")

    expected_data = json.dumps({"old_field": "old", "field": "value"})
    mock_redis.set.assert_called_once_with("verify:Venya", expected_data)


@pytest.mark.asyncio
async def test_update_field_with_new_exp_int(repo, mock_redis):
    mock_redis.get.return_value = json.dumps({"old_field": "old"}).encode("utf-8")

    await repo.update_field("Venya", "field", "value", new_exp=5)

    expected_data = json.dumps({"old_field": "old", "field": "value"})
    mock_redis.set.assert_called_once_with("verify:Venya", expected_data, ex=300)


@pytest.mark.asyncio
async def test_update_field_with_new_exp_timedelta(repo, mock_redis):
    mock_redis.get.return_value = json.dumps({"old_field": "old"}).encode("utf-8")

    await repo.update_field("Venya", "field", "value", new_exp=timedelta(minutes=10))

    expected_data = json.dumps({"old_field": "old", "field": "value"})
    mock_redis.set.assert_called_once_with("verify:Venya", expected_data, ex=600)
