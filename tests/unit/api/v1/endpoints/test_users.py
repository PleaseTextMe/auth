import pytest


@pytest.mark.asyncio
async def test_get_all_users(test_client, mock_user_service, valid_user):
    mock_user_service.get_all.return_value = [valid_user]
    response = await test_client.get("/api/v1/users/")
    assert response.status_code == 200
    assert response.json() == [{"username": "testuser", "public_bundle": {"key": "val"}}]
    mock_user_service.get_all.assert_called_once()
