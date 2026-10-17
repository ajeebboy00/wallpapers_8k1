import uuid
import pytest
from httpx import AsyncClient
from fastapi import status

async def create_test_wallpaper(client: AsyncClient, admin_headers: dict) -> dict:
    cat_resp = await client.get("/api/v1/categories")
    category_id = cat_resp.json()["data"][0]["id"]
    uid = uuid.uuid4().hex[:6]
    payload = {
        "title": f"Action Test Wallpaper {uid}",
        "description": "8K Interactive wallpaper",
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
        "tags": ["action", "test"]
    }
    resp = await client.post("/api/v1/wallpapers", json=payload, headers=admin_headers)
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.json()["data"]

@pytest.mark.asyncio
async def test_toggle_favorite_flow(client: AsyncClient, user_headers: dict, admin_headers: dict):
    """Test 1: Favorite addition, check, and deletion flow with counter updates."""
    wp = await create_test_wallpaper(client, admin_headers)
    wp_id = wp["id"]

    # 1. Initially check favorite status -> False
    check_resp1 = await client.get(f"/api/v1/wallpapers/{wp_id}/favorite", headers=user_headers)
    assert check_resp1.status_code == status.HTTP_200_OK
    assert check_resp1.json()["data"]["is_favorite"] is False

    # 2. Add to favorites
    add_resp = await client.post(f"/api/v1/wallpapers/{wp_id}/favorite", headers=user_headers)
    assert add_resp.status_code == status.HTTP_200_OK
    add_body = add_resp.json()
    assert add_body["success"] is True
    assert add_body["data"]["is_favorite"] is True
    assert add_body["data"]["favorite_count"] == 1

    # 3. Check status -> True
    check_resp2 = await client.get(f"/api/v1/wallpapers/{wp_id}/favorite", headers=user_headers)
    assert check_resp2.status_code == status.HTTP_200_OK
    assert check_resp2.json()["data"]["is_favorite"] is True

    # 4. Remove from favorites
    del_resp = await client.delete(f"/api/v1/wallpapers/{wp_id}/favorite", headers=user_headers)
    assert del_resp.status_code == status.HTTP_200_OK
    del_body = del_resp.json()
    assert del_body["success"] is True
    assert del_body["data"]["is_favorite"] is False
    assert del_body["data"]["favorite_count"] == 0

    # 5. Check status -> False
    check_resp3 = await client.get(f"/api/v1/wallpapers/{wp_id}/favorite", headers=user_headers)
    assert check_resp3.status_code == status.HTTP_200_OK
    assert check_resp3.json()["data"]["is_favorite"] is False

@pytest.mark.asyncio
async def test_favorite_requires_authentication(client: AsyncClient, admin_headers: dict):
    """Test 2: Modifying favorites unauthenticated returns 401."""
    wp = await create_test_wallpaper(client, admin_headers)
    wp_id = wp["id"]

    resp = await client.post(f"/api/v1/wallpapers/{wp_id}/favorite")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    del_resp = await client.delete(f"/api/v1/wallpapers/{wp_id}/favorite")
    assert del_resp.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_record_download_anonymous_and_authenticated(
    client: AsyncClient,
    user_headers: dict,
    admin_headers: dict
):
    """Test 3: Downloads increment download_count for both guests and authenticated users."""
    wp = await create_test_wallpaper(client, admin_headers)
    wp_id = wp["id"]

    # Anonymous download
    anon_resp = await client.post(f"/api/v1/wallpapers/{wp_id}/download")
    assert anon_resp.status_code == status.HTTP_200_OK
    anon_body = anon_resp.json()
    assert anon_body["success"] is True
    assert anon_body["data"]["download_count"] == 1
    assert anon_body["data"]["download_url"] == wp["original_url"]

    # Authenticated download
    auth_resp = await client.post(f"/api/v1/wallpapers/{wp_id}/download", headers=user_headers)
    assert auth_resp.status_code == status.HTTP_200_OK
    auth_body = auth_resp.json()
    assert auth_body["data"]["download_count"] == 2

@pytest.mark.asyncio
async def test_record_view(client: AsyncClient, admin_headers: dict):
    """Test 4: Recording a view increments view_count."""
    wp = await create_test_wallpaper(client, admin_headers)
    wp_id = wp["id"]

    view_resp = await client.post(
        f"/api/v1/wallpapers/{wp_id}/view",
        json={"session_identifier": "test-session-123"}
    )
    assert view_resp.status_code == status.HTTP_200_OK
    assert view_resp.json()["data"]["view_count"] == 1

@pytest.mark.asyncio
async def test_record_share(client: AsyncClient, admin_headers: dict):
    """Test 5: Recording a share increments share_count."""
    wp = await create_test_wallpaper(client, admin_headers)
    wp_id = wp["id"]

    share_resp = await client.post(
        f"/api/v1/wallpapers/{wp_id}/share",
        json={"platform": "whatsapp"}
    )
    assert share_resp.status_code == status.HTTP_200_OK
    assert share_resp.json()["data"]["share_count"] == 1

@pytest.mark.asyncio
async def test_report_wallpaper(client: AsyncClient, user_headers: dict, admin_headers: dict):
    """Test 6: User can report wallpaper with reason and description."""
    wp = await create_test_wallpaper(client, admin_headers)
    wp_id = wp["id"]

    report_payload = {
        "reason": "COPYRIGHT",
        "description": "Unauthorized use of digital artwork"
    }
    resp = await client.post(
        f"/api/v1/wallpapers/{wp_id}/report",
        json=report_payload,
        headers=user_headers
    )
    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["reason"] == "COPYRIGHT"
    assert body["data"]["status"] == "PENDING"

@pytest.mark.asyncio
async def test_get_my_favorites_and_downloads_endpoints(
    client: AsyncClient,
    user_headers: dict,
    admin_headers: dict
):
    """Test 7: User can fetch personal favorites and downloads libraries."""
    wp1 = await create_test_wallpaper(client, admin_headers)
    wp2 = await create_test_wallpaper(client, admin_headers)

    # Favorite wp1
    await client.post(f"/api/v1/wallpapers/{wp1['id']}/favorite", headers=user_headers)
    # Download wp2
    await client.post(f"/api/v1/wallpapers/{wp2['id']}/download", headers=user_headers)

    # Fetch favorites
    favs_resp = await client.get("/api/v1/users/me/favorites", headers=user_headers)
    assert favs_resp.status_code == status.HTTP_200_OK
    fav_ids = [item["id"] for item in favs_resp.json()["data"]]
    assert wp1["id"] in fav_ids

    # Fetch downloads
    dl_resp = await client.get("/api/v1/users/me/downloads", headers=user_headers)
    assert dl_resp.status_code == status.HTTP_200_OK
    dl_ids = [item["id"] for item in dl_resp.json()["data"]]
    assert wp2["id"] in dl_ids
