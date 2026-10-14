import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import fakeredis.aioredis
import pytest
from sqlalchemy.engine import make_url

from src.core.config import PostgresSettings
from src.domain.exceptions import (
    UserEmailAlreadyExists,
    VerificationDeliveryUnavailable,
    VerifyCodeNotConfirmed,
)
from src.infrastructure.email import send_verification_email
from src.infrastructure.handlers.exceptions import exception_handlers
from src.infrastructure.repositories.verify import RedisVerifyRepository
from src.services.user import UserService
from src.services.verify import VerifyService


@pytest.mark.asyncio
async def test_verified_token_cannot_register_another_email(mock_uow):
    from src.domain.dtos.user import UserCreateDTO

    data = UserCreateDTO(
        email="victim@example.com", username="victim", password="password123",
        verify_token="attacker-token", public_bundle={"bundle_json": "{}", "signature": "sig"},
        vault={"encrypted_payload": "enc", "nonce": "nonce", "auth_tag": "tag"},
    )
    mock_uow.user_repository.get_by_email.return_value = None
    mock_uow.verify_repository.get_value.return_value = json.dumps(
        {"status": "verified", "email": "attacker@example.com"}
    )
    with pytest.raises(VerifyCodeNotConfirmed):
        await UserService(mock_uow).create(data)
    mock_uow.user_repository.create.assert_not_awaited()
    mock_uow.verify_repository.delete_value.assert_not_awaited()


@pytest.mark.asyncio
async def test_failed_commit_rolls_back_and_closes(mock_session, mock_redis):
    from src.infrastructure.uow import DatabaseUnitOfWork

    mock_session.commit.side_effect = RuntimeError("database unavailable")
    with pytest.raises(RuntimeError):
        async with DatabaseUnitOfWork(mock_session, mock_redis):
            pass
    mock_session.rollback.assert_awaited_once()
    mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_delivery_failure_does_not_leave_a_usable_token(mock_uow):
    mock_uow.user_repository.get_by_email.return_value = None
    with patch("src.services.verify.send_verification_email", new_callable=AsyncMock) as delivery:
        delivery.side_effect = VerificationDeliveryUnavailable()
        with pytest.raises(VerificationDeliveryUnavailable):
            await VerifyService(mock_uow).create_email_code("user@example.com")
    key = mock_uow.verify_repository.set_value.call_args.kwargs["key"]
    mock_uow.verify_repository.delete_value.assert_awaited_once_with(key)


@pytest.mark.asyncio
async def test_unconfigured_email_delivery_fails_closed():
    with patch("src.infrastructure.email.settings", SimpleNamespace(email=SimpleNamespace(host="", sender=""))):
        with pytest.raises(VerificationDeliveryUnavailable):
            await send_verification_email("user@example.com", 123456)


@pytest.mark.asyncio
async def test_verification_lua_binds_email_and_limits_concurrent_guesses():
    async with fakeredis.aioredis.FakeRedis() as redis:
        repo = RedisVerifyRepository(redis)
        payload = json.dumps({"email": "owner@example.com", "code": 123456, "status": "pending"})
        await repo.set_value("token", payload, exp=5)
        assert await repo.verify_code("token", "other@example.com", 123456) == 0
        assert await repo.verify_code("token", "owner@example.com", 123456) == 1
        assert json.loads(await repo.get_value("token"))["status"] == "verified"
        await redis.expire("verify:token", 60)
        assert await repo.verify_code("token", "owner@example.com", 123456) == 1
        assert await redis.ttl("verify:token") <= 60  # Cannot extend a verified token.

        await repo.set_value("guesses", payload, exp=5)
        results = await asyncio.gather(*(
            repo.verify_code("guesses", "owner@example.com", 111111) for _ in range(10)
        ))
        assert results.count(0) == 5
        assert results.count(-1) == 5
        assert await repo.verify_code("guesses", "owner@example.com", 123456) == -1
        assert await repo.get_value("guesses") is None


@pytest.mark.asyncio
async def test_domain_error_is_an_http_response(test_app, test_client, mock_user_service):
    for exception, handler in exception_handlers.items():
        test_app.add_exception_handler(exception, handler)
    # Middleware is initialized on the first request, after handlers are registered.
    mock_user_service.create.side_effect = UserEmailAlreadyExists()
    response = await test_client.post("/api/v1/auth/register/", json={
        "email": "user@example.com", "username": "user", "password": "password123",
        "verify_token": "token", "public_bundle": {"bundle_json": "{}", "signature": "sig"},
        "vault": {"encrypted_payload": "enc", "nonce": "nonce", "auth_tag": "tag"},
    })
    assert response.status_code == 409
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_login_without_user_agent_uses_client_ip(test_client, mock_session_service):
    test_client.headers.pop("user-agent", None)
    response = await test_client.post("/api/v1/auth/login/", json={
        "email": "user@example.com", "password": "password123",
    }, headers={"host": "attacker.invalid"})
    assert response.status_code == 200
    dto = mock_session_service.create.call_args.args[0]
    assert dto.user_agent == "unknown"
    assert dto.user_ip == "127.0.0.1"


@pytest.mark.parametrize("password", ["p@ss:word/with%chars#", "space password"])
def test_database_url_preserves_reserved_password_characters(password):
    pg = PostgresSettings(_env_file=None, POSTGRES_PASSWORD=password)
    assert make_url(pg.connection_url).password == password
    assert make_url(pg.connection_url_2).password == password


def test_production_settings_do_not_load_test_environment(tmp_path):
    (tmp_path / ".env.test").write_text("POSTGRES_DB=wrong_test_database\n")
    env = os.environ.copy()
    for name in list(env):
        if name.startswith("POSTGRES_") or name == "ENV_FILE":
            env.pop(name)
    env["POSTGRES_PASSWORD"] = "test-password-unused"
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])
    result = subprocess.run(
        [sys.executable, "-c", "from src.core.config import settings; print(settings.postgres.db_name)"],
        cwd=tmp_path, env=env, capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "please_text_me_db"
