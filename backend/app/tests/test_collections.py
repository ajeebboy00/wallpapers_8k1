import uuid
import pytest
from httpx import AsyncClient
from fastapi import status

async def create_sample_wallpaper(client: AsyncClient, admin_headers: dict) -> str:
    """Helper to create a wallpaper and return its UUID."""
    cat_resp = await client.get("/api/v1/categories")
    cat_id = cat_resp.json()["data"][0]["id"]
    uid = uuid.uuid4().hex[:6]

    resp = await client.post("/api/v1/wallpapers", json={
        "title": f"Collection Item {uid}",
        "category_id": cat_id,
        "original_url": "https://storage.wallpapers8k1.com/1.png",
        "image_url": "https://storage.wallpapers8k1.com/1.webp",
        "thumbnail_url": "https://storage.wallpapers8k1.com/1_thumb.webp",
        "preview_url": "https://storage.wallpapers8k1.com/1_prev.webp",
        "width": 7680,
        "height": 4320,
        "file_size": 1000000,
        "file_format": "webp",
        "resolution": "8K"
    }, headers=admin_headers)
    return resp.json()["data"]["id"]

@pytest.mark.asyncio
async def test_create_collection_admin_success(client: AsyncClient, admin_headers: dict):
    """Test 1: Admin creates a collection with ordered wallpapers."""
    wp_id_1 = await create_sample_wallpaper(client, admin_headers)
    wp_id_2 = await create_sample_wallpaper(client, admin_headers)
    uid = uuid.uuid4().hex[:6]

    payload = {
        "name": f"Cyberpunk Vistas {uid}",
        "description": "Curated collection of 8K neon cityscapes",
        "cover_image_url": "https://storage.wallpapers8k1.com/covers/cyber.webp",
        "is_featured": True,
        "is_published": True,
        "wallpaper_ids": [wp_id_1, wp_id_2]
    }

    response = await client.post("/api/v1/collections", json=payload, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["success"] is True
    assert body["data"]["name"] == payload["name"]
    assert f"cyberpunk-vistas-{uid}" in body["data"]["slug"]
    assert body["data"]["wallpaper_count"] == 2
    assert body["data"]["is_featured"] is True

@pytest.mark.asyncio
async def test_create_collection_forbidden_for_user(client: AsyncClient, user_headers: dict):
    """Test 2: Standard user cannot create collections (403 FORBIDDEN_ROLE)."""
    payload = {
        "name": "User Collection Attempt"
    }
    response = await client.post("/api/v1/collections", json=payload, headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"]["code"] == "FORBIDDEN_ROLE"

@pytest.mark.asyncio
async def test_list_collections_pagination(client: AsyncClient, admin_headers: dict):
    """Test 3: GET /api/v1/collections returns paginated results."""
    uid = uuid.uuid4().hex[:6]
    await client.post("/api/v1/collections", json={
        "name": f"Paginated Collection {uid}"
    }, headers=admin_headers)

    response = await client.get("/api/v1/collections?page=1&limit=5")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert "meta" in body
    assert body["meta"]["page"] == 1
    assert len(body["data"]) >= 1

@pytest.mark.asyncio
async def test_get_collection_details_with_wallpapers(client: AsyncClient, admin_headers: dict):
    """Test 4: GET /api/v1/collections/{slug} returns collection with wallpapers in order."""
    wp_id_1 = await create_sample_wallpaper(client, admin_headers)
    wp_id_2 = await create_sample_wallpaper(client, admin_headers)
    uid = uuid.uuid4().hex[:6]

    create_resp = await client.post("/api/v1/collections", json={
        "name": f"Deep Cosmos {uid}",
        "wallpaper_ids": [wp_id_1, wp_id_2]
    }, headers=admin_headers)
    coll_slug = create_resp.json()["data"]["slug"]

    response = await client.get(f"/api/v1/collections/{coll_slug}")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["slug"] == coll_slug
    assert len(data["wallpapers"]) == 2
    assert data["wallpapers"][0]["id"] == wp_id_1
    assert data["wallpapers"][1]["id"] == wp_id_2

@pytest.mark.asyncio
async def test_get_collection_not_found(client: AsyncClient):
    """Test 5: Non-existent collection slug returns 404 COLLECTION_NOT_FOUND."""
    response = await client.get("/api/v1/collections/nonexistent-collection-slug-xyz")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["error"]["code"] == "COLLECTION_NOT_FOUND"

@pytest.mark.asyncio
async def test_update_collection_admin(client: AsyncClient, admin_headers: dict):
    """Test 6: Admin updates collection metadata and reorders wallpapers."""
    wp_id_1 = await create_sample_wallpaper(client, admin_headers)
    wp_id_2 = await create_sample_wallpaper(client, admin_headers)
    uid = uuid.uuid4().hex[:6]

    create_resp = await client.post("/api/v1/collections", json={
        "name": f"Initial Coll {uid}",
        "wallpaper_ids": [wp_id_1]
    }, headers=admin_headers)
    coll_id = create_resp.json()["data"]["id"]

    # Reorder and add second wallpaper
    update_resp = await client.put(
        f"/api/v1/collections/{coll_id}",
        json={"name": f"Updated Coll {uid}", "wallpaper_ids": [wp_id_2, wp_id_1]},
        headers=admin_headers
    )
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["data"]["name"] == f"Updated Coll {uid}"
    assert update_resp.json()["data"]["wallpaper_count"] == 2

    # Check order in detail
    get_resp = await client.get(f"/api/v1/collections/{coll_id}")
    wallpapers = get_resp.json()["data"]["wallpapers"]
    assert wallpapers[0]["id"] == wp_id_2
    assert wallpapers[1]["id"] == wp_id_1

@pytest.mark.asyncio
async def test_delete_collection_admin(client: AsyncClient, admin_headers: dict):
    """Test 7: Admin deletes collection; member wallpapers remain intact."""
    wp_id = await create_sample_wallpaper(client, admin_headers)
    uid = uuid.uuid4().hex[:6]

    create_resp = await client.post("/api/v1/collections", json={
        "name": f"Deletable Coll {uid}",
        "wallpaper_ids": [wp_id]
    }, headers=admin_headers)
    coll_id = create_resp.json()["data"]["id"]

    # Delete collection
    del_resp = await client.delete(f"/api/v1/collections/{coll_id}", headers=admin_headers)
    assert del_resp.status_code == status.HTTP_200_OK
    assert del_resp.json()["data"]["deleted"] is True

    # Collection is gone
    get_coll = await client.get(f"/api/v1/collections/{coll_id}")
    assert get_coll.status_code == status.HTTP_404_NOT_FOUND

    # Underlying wallpaper still exists!
    get_wp = await client.get(f"/api/v1/wallpapers/{wp_id}")
    assert get_wp.status_code == status.HTTP_200_OK
