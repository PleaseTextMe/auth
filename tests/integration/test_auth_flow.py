import httpx
import pytest
from sqlalchemy import text

from src.infrastructure.db.postgres import get_session


@pytest.mark.integration
@pytest.mark.asyncio
async def test_healthcheck(client: httpx.AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_user_adds_to_db(client: httpx.AsyncClient):
    import uuid

    suffix = str(uuid.uuid4())[:8]
    email = f"integration_db_{suffix}@test.com"
    username = f"integrationdb_{suffix}"

    response = await client.post("/api/v1/auth/send-verify-code/", json={"email": email})
    assert response.status_code == 200
    verify_token = response.json()["verify_token"]

    response = await client.post(
        "/api/v1/auth/check-verify-code/",
        json={"email": email, "code": 666666, "verify_token": verify_token},
    )
    assert response.status_code == 200

    payload = {
        "email": email,
        "username": username,
        "password": "Password123!",
        "verify_token": verify_token,
        "public_bundle": {"bundle_json": "{}", "signature": "sig"},
        "vault": {"encrypted_payload": "enc", "nonce": "nonce", "auth_tag": "tag"},
    }
    response = await client.post(
        "/api/v1/auth/register/", json=payload, headers={"user-agent": "test", "host": "127.0.0.1"}
    )
    assert response.status_code == 201

    async with get_session() as session:
        result = await session.execute(
            text(f"SELECT email, username FROM \"user\" WHERE email = '{email}'")
        )
        user = result.fetchone()
        assert user is not None
        assert user[0] == email
        assert user[1] == username
