import uuid
import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.constants import NotificationType

async def create_test_wallpaper_for_daily(client: AsyncClient, admin_headers: dict) -> dict:
    cat_resp = await client.get("/api/v1/categories")
    category_id = cat_resp.json()["data"][0]["id"]
    uid = uuid.uuid4().hex[:6]
    payload = {
        "title": f"Spotlight Test Wallpaper {uid}",
        "description": "Daily notification spotlight test",
        "category_id": category_id,
        "original_url": f"https://storage.wallpapers8k1.com/raw/{uid}.png",
        "image_url": f"https://storage.wallpapers8k1.com/opt/{uid}.webp",
        "thumbnail_url": f"https://storage.wallpapers8k1.com/thumb/{uid}.webp",
        "preview_url": f"https://storage.wallpapers8k1.com/prev/{uid}.webp",
        "width": 7680,
        "height": 4320,
        "file_size": 25000000,
        "file_format": "webp",
        "resolution": "8K",
        "is_published": True,
        "is_daily": True,
        "tags": ["daily", "test"]
    }
    resp = await client.post("/api/v1/wallpapers", json=payload, headers=admin_headers)
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.json()["data"]

@pytest.mark.asyncio
async def test_register_device_token_anonymous(client: AsyncClient):
    """Test 1: Anonymous device token registration and topic assignment."""
    token_str = f"fcm_anon_token_{uuid.uuid4().hex}"
    payload = {
        "token": token_str,
        "device_id": "android_pixel_8_pro_test",
        "platform": "android",
        "app_version": "1.0.0",
        "topics": ["daily_wallpaper", "featured"]
    }
    resp = await client.post("/api/v1/notifications/devices", json=payload)
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["token"] == token_str
    assert data["platform"] == "android"
    assert data["is_active"] is True
    assert "daily_wallpaper" in data["topics"]

@pytest.mark.asyncio
async def test_register_device_token_authenticated(client: AsyncClient, user_headers: dict):
    """Test 2: Authenticated user device registration and token ownership update."""
    token_str = f"fcm_user_token_{uuid.uuid4().hex}"
    payload = {
        "token": token_str,
        "device_id": "android_samsung_s24_ultra",
        "platform": "android",
        "app_version": "1.0.1",
        "topics": ["all"]
    }
    resp = await client.post("/api/v1/notifications/devices", json=payload, headers=user_headers)
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["user_id"] is not None

@pytest.mark.asyncio
async def test_unregister_device_token(client: AsyncClient):
    """Test 3: Device push token unregistration and deactivation."""
    token_str = f"fcm_deact_token_{uuid.uuid4().hex}"
    # Register first
    await client.post(
        "/api/v1/notifications/devices",
        json={"token": token_str, "platform": "android"}
    )

    # Unregister
    resp = await client.delete(f"/api/v1/notifications/devices/{token_str}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["unregistered"] is True

@pytest.mark.asyncio
async def test_inbox_notifications_flow(
    client: AsyncClient,
    user_headers: dict,
    admin_headers: dict
):
    """Test 4: Broadcast to inbox, unread count calculation, and pagination."""
    # 1. Initially check unread count
    count_resp1 = await client.get("/api/v1/notifications/unread-count", headers=user_headers)
    assert count_resp1.status_code == status.HTTP_200_OK
    initial_count = count_resp1.json()["data"]["unread_count"]

    # 2. Admin broadcasts a notification saving to inbox
    broadcast_payload = {
        "title": "Welcome to W8K1 Stage 13",
        "message": "Experience ultra-high fidelity notifications system.",
        "type": NotificationType.SYSTEM.value,
        "save_to_inbox": True
    }
    b_resp = await client.post(
        "/api/v1/notifications/admin/broadcast",
        json=broadcast_payload,
        headers=admin_headers
    )
    assert b_resp.status_code == status.HTTP_200_OK
    assert b_resp.json()["data"]["success"] is True

    # 3. Unread count should increment
    count_resp2 = await client.get("/api/v1/notifications/unread-count", headers=user_headers)
    assert count_resp2.status_code == status.HTTP_200_OK
    new_count = count_resp2.json()["data"]["unread_count"]
    assert new_count >= initial_count + 1

    # 4. List notifications
    list_resp = await client.get("/api/v1/notifications?page=1&limit=10", headers=user_headers)
    assert list_resp.status_code == status.HTTP_200_OK
    items = list_resp.json()["data"]
    assert len(items) >= 1
    target_notif = items[0]
    assert "title" in target_notif
    assert "message" in target_notif
    assert "is_read" in target_notif

@pytest.mark.asyncio
async def test_mark_notification_read_and_read_all(
    client: AsyncClient,
    user_headers: dict,
    admin_headers: dict
):
    """Test 5: Mark individual notification as read and bulk mark all read."""
    # 1. Admin sends broadcast to ensure at least one unread exists
    await client.post(
        "/api/v1/notifications/admin/broadcast",
        json={
            "title": "Mark Read Test Alert",
            "message": "Testing read status changes",
            "type": NotificationType.FEATURED.value,
            "save_to_inbox": True
        },
        headers=admin_headers
    )

    # 2. Get list of notifications
    list_resp = await client.get("/api/v1/notifications", headers=user_headers)
    items = list_resp.json()["data"]
    assert len(items) >= 1
    first_id = items[0]["id"]

    # 3. Mark single as read
    read_resp = await client.patch(f"/api/v1/notifications/{first_id}/read", headers=user_headers)
    assert read_resp.status_code == status.HTTP_200_OK
    assert read_resp.json()["data"]["is_read"] is True

    # 4. Mark all as read
    all_read_resp = await client.patch("/api/v1/notifications/read-all", headers=user_headers)
    assert all_read_resp.status_code == status.HTTP_200_OK

    # 5. Check unread count is now 0
    count_resp = await client.get("/api/v1/notifications/unread-count", headers=user_headers)
    assert count_resp.json()["data"]["unread_count"] == 0

@pytest.mark.asyncio
async def test_admin_broadcast_access_control(
    client: AsyncClient,
    user_headers: dict,
    admin_headers: dict
):
    """Test 6: RBAC protection on administrative notification broadcasts."""
    payload = {
        "title": "Unauthorized Test",
        "message": "Should be rejected",
        "type": NotificationType.SYSTEM.value
    }

    # 1. Standard user receives 403 Forbidden
    resp_forbidden = await client.post(
        "/api/v1/notifications/admin/broadcast",
        json=payload,
        headers=user_headers
    )
    assert resp_forbidden.status_code == status.HTTP_403_FORBIDDEN

    # 2. Admin succeeds
    resp_ok = await client.post(
        "/api/v1/notifications/admin/broadcast",
        json=payload,
        headers=admin_headers
    )
    assert resp_ok.status_code == status.HTTP_200_OK
    assert resp_ok.json()["data"]["delivery_mode"] in ["fcm_live", "fcm_mock_fallback"]

@pytest.mark.asyncio
async def test_daily_wallpaper_spotlight_alert(
    client: AsyncClient,
    admin_headers: dict
):
    """Test 7: Dispatch automated daily spotlight push notification."""
    wp = await create_test_wallpaper_for_daily(client, admin_headers)
    wp_id = wp["id"]

    resp = await client.post(
        f"/api/v1/notifications/admin/daily-spotlight?wallpaper_id={wp_id}",
        headers=admin_headers
    )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["success"] is True
    assert data["sent_count"] >= 0
