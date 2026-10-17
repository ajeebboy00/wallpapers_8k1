import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_get_my_profile_success(client: AsyncClient, user_headers: dict):
    """Test 1: Authenticated user can fetch personal profile with counters."""
    resp = await client.get("/api/v1/users/me", headers=user_headers)
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "email" in data
    assert "name" in data
    assert "favorites_count" in data
    assert "downloads_count" in data

@pytest.mark.asyncio
async def test_update_my_profile_success(client: AsyncClient, user_headers: dict):
    """Test 2: User can update name and profile image."""
    payload = {
        "name": "Updated Explorer Name",
        "profile_image_url": "https://storage.wallpapers8k1.com/avatars/user.webp"
    }
    resp = await client.put("/api/v1/users/me", json=payload, headers=user_headers)
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["name"] == "Updated Explorer Name"
    assert body["data"]["profile_image_url"] == "https://storage.wallpapers8k1.com/avatars/user.webp"

@pytest.mark.asyncio
async def test_change_password_success_and_failure(client: AsyncClient, user_headers: dict):
    """Test 3: User can change password with correct current password; rejects invalid current."""
    # Invalid current password
    fail_resp = await client.put(
        "/api/v1/users/me/password",
        json={"current_password": "WrongPassword123!", "new_password": "NewValidPassword999!"},
        headers=user_headers
    )
    assert fail_resp.status_code == status.HTTP_401_UNAUTHORIZED

    # Valid change
    success_resp = await client.put(
        "/api/v1/users/me/password",
        json={"current_password": "UserPass123!", "new_password": "NewValidPassword999!"},
        headers=user_headers
    )
    assert success_resp.status_code == status.HTTP_200_OK
    assert success_resp.json()["success"] is True

@pytest.mark.asyncio
async def test_notification_preferences_get_and_update(client: AsyncClient, user_headers: dict):
    """Test 4: User can inspect and toggle notification preferences."""
    # Get preferences
    get_resp = await client.get("/api/v1/users/me/notification-preferences", headers=user_headers)
    assert get_resp.status_code == status.HTTP_200_OK
    body = get_resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "daily_wallpaper" in data
    assert "new_wallpapers" in data

    # Update preferences
    update_payload = {
        "daily_wallpaper": False,
        "promotional": True
    }
    put_resp = await client.put(
        "/api/v1/users/me/notification-preferences",
        json=update_payload,
        headers=user_headers
    )
    assert put_resp.status_code == status.HTTP_200_OK
    put_body = put_resp.json()
    assert put_body["success"] is True
    assert put_body["data"]["daily_wallpaper"] is False
    assert put_body["data"]["promotional"] is True
