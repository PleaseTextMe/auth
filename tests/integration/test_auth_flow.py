import httpx
import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_healthcheck(client: httpx.AsyncClient):
    # Depending on what endpoints are available. We just test 404 on root for now to ensure app is alive
    response = await client.get("/api/openapi.json")
    assert response.status_code == 200
