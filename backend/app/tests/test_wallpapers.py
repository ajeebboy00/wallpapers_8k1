import uuid
import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category

async def get_test_category_id(client: AsyncClient) -> str:
    """Helper to fetch a valid seeded category ID."""
    resp = await client.get("/api/v1/categories")
    categories = resp.json()["data"]
    return categories[0]["id"]

@pytest.mark.asyncio
async def test_create_wallpaper_admin_success(client: AsyncClient, admin_headers: dict):
    """Test 1: Admin can create a wallpaper with metadata, auto-slug, aspect ratio, and tags."""
    category_id = await get_test_category_id(client)
    uid = uuid.uuid4().hex[:6]

    payload = {
        "title": f"Nebula Cosmic Dust {uid}",
        "description": "8K Deep space vista with cosmic dust and vibrant stars",
        "category_id": category_id,
        "original_url": "https://storage.wallpapers8k1.com/raw/cosmic.png",
        "image_url": "https://storage.wallpapers8k1.com/optimized/cosmic.webp",
        "thumbnail_url": "https://storage.wallpapers8k1.com/thumbs/cosmic.webp",
        "preview_url": "https://storage.wallpapers8k1.com/previews/cosmic.webp",
        "width": 7680,
        "height": 4320,
        "file_size": 24500000,
        "file_format": "webp",
        "resolution": "8K",
        "is_featured": True,
        "is_trending": False,
        "is_daily": False,
        "is_published": True,
        "tags": ["space", "cosmos", f"tag_{uid}"]
    }

    response = await client.post("/api/v1/wallpapers", json=payload, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["success"] is True
    data = body["data"]

    assert data["title"] == payload["title"]
    assert f"nebula-cosmic-dust-{uid}" in data["slug"]
    assert data["aspect_ratio"] == 1.7778  # 7680 / 4320
    assert data["category_id"] == category_id
    assert data["category"] is not None
    assert data["category"]["id"] == category_id
    assert len(data["tags"]) == 3
    tag_names = [t["name"] for t in data["tags"]]
    assert "space" in tag_names
    assert "cosmos" in tag_names

@pytest.mark.asyncio
async def test_create_wallpaper_invalid_category(client: AsyncClient, admin_headers: dict):
    """Test 2: Creating wallpaper with invalid category ID returns 404 CATEGORY_NOT_FOUND."""
    fake_category_id = str(uuid.uuid4())
    payload = {
        "title": "Invalid Cat WP",
        "category_id": fake_category_id,
        "original_url": "https://storage.wallpapers8k1.com/raw/1.png",
        "image_url": "https://storage.wallpapers8k1.com/1.webp",
        "thumbnail_url": "https://storage.wallpapers8k1.com/1_thumb.webp",
        "preview_url": "https://storage.wallpapers8k1.com/1_prev.webp",
        "width": 3840,
        "height": 2160,
        "file_size": 12000000,
        "file_format": "webp",
        "resolution": "4K"
    }
    response = await client.post("/api/v1/wallpapers", json=payload, headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body["error"]["code"] == "CATEGORY_NOT_FOUND"

@pytest.mark.asyncio
async def test_create_wallpaper_forbidden_for_user(client: AsyncClient, user_headers: dict):
    """Test 3: Regular users cannot create wallpapers (403 FORBIDDEN_ROLE)."""
    category_id = await get_test_category_id(client)
    payload = {
        "title": "Unauthorized Wallpaper",
        "category_id": category_id,
        "original_url": "https://storage.wallpapers8k1.com/raw/1.png",
        "image_url": "https://storage.wallpapers8k1.com/1.webp",
        "thumbnail_url": "https://storage.wallpapers8k1.com/1_thumb.webp",
        "preview_url": "https://storage.wallpapers8k1.com/1_prev.webp",
        "width": 3840,
        "height": 2160,
        "file_size": 12000000,
        "file_format": "webp",
        "resolution": "4K"
    }
    response = await client.post("/api/v1/wallpapers", json=payload, headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"]["code"] == "FORBIDDEN_ROLE"

@pytest.mark.asyncio
async def test_list_wallpapers_pagination(client: AsyncClient, admin_headers: dict):
    """Test 4: GET /api/v1/wallpapers returns paginated structure."""
    category_id = await get_test_category_id(client)

    # Ensure at least 2 wallpapers exist
    for i in range(2):
        uid = uuid.uuid4().hex[:6]
        await client.post("/api/v1/wallpapers", json={
            "title": f"Paginated WP {i} {uid}",
            "category_id": category_id,
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

    response = await client.get("/api/v1/wallpapers?page=1&limit=1")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert "meta" in body
    assert body["meta"]["page"] == 1
    assert body["meta"]["limit"] == 1
    assert body["meta"]["total"] >= 2
    assert body["meta"]["total_pages"] >= 2
    assert len(body["data"]) == 1

@pytest.mark.asyncio
async def test_filter_wallpapers_by_resolution(client: AsyncClient, admin_headers: dict):
    """Test 5: Filter wallpapers by resolution (e.g. 8K vs 4K)."""
    category_id = await get_test_category_id(client)
    uid = uuid.uuid4().hex[:6]

    # Create 8K wallpaper
    await client.post("/api/v1/wallpapers", json={
        "title": f"Specific 8K WP {uid}",
        "category_id": category_id,
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

    response = await client.get("/api/v1/wallpapers?resolution=8K")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    for wp in body["data"]:
        assert wp["resolution"] == "8K"

@pytest.mark.asyncio
async def test_filter_wallpapers_by_category_slug(client: AsyncClient, admin_headers: dict):
    """Test 6: Filter wallpapers by category slug."""
    # Fetch nature category
    cat_resp = await client.get("/api/v1/categories/nature")
    assert cat_resp.status_code == status.HTTP_200_OK
    nature_id = cat_resp.json()["data"]["id"]

    uid = uuid.uuid4().hex[:6]
    await client.post("/api/v1/wallpapers", json={
        "title": f"Nature Mountain {uid}",
        "category_id": nature_id,
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

    response = await client.get("/api/v1/wallpapers?category=nature")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body["data"]) >= 1
    for item in body["data"]:
        assert item["category"]["slug"] == "nature"

@pytest.mark.asyncio
async def test_get_daily_wallpaper_flow(client: AsyncClient, admin_headers: dict):
    """Test 7: Set wallpaper as daily and retrieve via /daily endpoint."""
    category_id = await get_test_category_id(client)
    uid = uuid.uuid4().hex[:6]

    create_resp = await client.post("/api/v1/wallpapers", json={
        "title": f"Today's Daily Pick {uid}",
        "category_id": category_id,
        "original_url": "https://storage.wallpapers8k1.com/1.png",
        "image_url": "https://storage.wallpapers8k1.com/1.webp",
        "thumbnail_url": "https://storage.wallpapers8k1.com/1_thumb.webp",
        "preview_url": "https://storage.wallpapers8k1.com/1_prev.webp",
        "width": 7680,
        "height": 4320,
        "file_size": 1000000,
        "file_format": "webp",
        "resolution": "8K",
        "is_daily": True
    }, headers=admin_headers)
    assert create_resp.status_code == status.HTTP_201_CREATED

    response = await client.get("/api/v1/wallpapers/daily")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    assert body["data"]["is_daily"] is True

@pytest.mark.asyncio
async def test_get_wallpaper_by_id_and_slug(client: AsyncClient, admin_headers: dict):
    """Test 8: Retrieve wallpaper by UUID and by slug."""
    category_id = await get_test_category_id(client)
    uid = uuid.uuid4().hex[:6]

    create_resp = await client.post("/api/v1/wallpapers", json={
        "title": f"Dual Identifier WP {uid}",
        "category_id": category_id,
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
    wp_data = create_resp.json()["data"]
    wp_id = wp_data["id"]
    wp_slug = wp_data["slug"]

    # 1. Fetch by UUID
    resp_id = await client.get(f"/api/v1/wallpapers/{wp_id}")
    assert resp_id.status_code == status.HTTP_200_OK
    assert resp_id.json()["data"]["id"] == wp_id

    # 2. Fetch by Slug
    resp_slug = await client.get(f"/api/v1/wallpapers/{wp_slug}")
    assert resp_slug.status_code == status.HTTP_200_OK
    assert resp_slug.json()["data"]["slug"] == wp_slug

@pytest.mark.asyncio
async def test_get_wallpaper_not_found(client: AsyncClient):
    """Test 9: Non-existent wallpaper returns 404 WALLPAPER_NOT_FOUND."""
    response = await client.get("/api/v1/wallpapers/nonexistent-wp-slug-xyz")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["error"]["code"] == "WALLPAPER_NOT_FOUND"

@pytest.mark.asyncio
async def test_get_related_wallpapers(client: AsyncClient, admin_headers: dict):
    """Test 10: GET /api/v1/wallpapers/{id}/related returns matching category/tag wallpapers."""
    category_id = await get_test_category_id(client)
    uid = uuid.uuid4().hex[:6]

    # Create target wallpaper
    target_resp = await client.post("/api/v1/wallpapers", json={
        "title": f"Target WP {uid}",
        "category_id": category_id,
        "original_url": "https://storage.wallpapers8k1.com/1.png",
        "image_url": "https://storage.wallpapers8k1.com/1.webp",
        "thumbnail_url": "https://storage.wallpapers8k1.com/1_thumb.webp",
        "preview_url": "https://storage.wallpapers8k1.com/1_prev.webp",
        "width": 7680,
        "height": 4320,
        "file_size": 1000000,
        "file_format": "webp",
        "resolution": "8K",
        "tags": [f"shared_tag_{uid}"]
    }, headers=admin_headers)
    target_id = target_resp.json()["data"]["id"]

    # Create related wallpaper in same category with shared tag
    await client.post("/api/v1/wallpapers", json={
        "title": f"Related WP {uid}",
        "category_id": category_id,
        "original_url": "https://storage.wallpapers8k1.com/2.png",
        "image_url": "https://storage.wallpapers8k1.com/2.webp",
        "thumbnail_url": "https://storage.wallpapers8k1.com/2_thumb.webp",
        "preview_url": "https://storage.wallpapers8k1.com/2_prev.webp",
        "width": 7680,
        "height": 4320,
        "file_size": 1000000,
        "file_format": "webp",
        "resolution": "8K",
        "tags": [f"shared_tag_{uid}"]
    }, headers=admin_headers)

    response = await client.get(f"/api/v1/wallpapers/{target_id}/related")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    related_ids = [w["id"] for w in body["data"]]
    assert target_id not in related_ids  # Should not include itself

@pytest.mark.asyncio
async def test_update_wallpaper_admin(client: AsyncClient, admin_headers: dict):
    """Test 11: Admin updates wallpaper title, tags, and flags."""
    category_id = await get_test_category_id(client)
    uid = uuid.uuid4().hex[:6]

    create_resp = await client.post("/api/v1/wallpapers", json={
        "title": f"Initial WP {uid}",
        "category_id": category_id,
        "original_url": "https://storage.wallpapers8k1.com/1.png",
        "image_url": "https://storage.wallpapers8k1.com/1.webp",
        "thumbnail_url": "https://storage.wallpapers8k1.com/1_thumb.webp",
        "preview_url": "https://storage.wallpapers8k1.com/1_prev.webp",
        "width": 7680,
        "height": 4320,
        "file_size": 1000000,
        "file_format": "webp",
        "resolution": "8K",
        "tags": ["initial_tag"]
    }, headers=admin_headers)
    wp_id = create_resp.json()["data"]["id"]

    update_resp = await client.put(
        f"/api/v1/wallpapers/{wp_id}",
        json={"title": f"Updated WP {uid}", "is_trending": True, "tags": ["initial_tag", "new_tag"]},
        headers=admin_headers
    )
    assert update_resp.status_code == status.HTTP_200_OK
    body = update_resp.json()
    assert body["data"]["title"] == f"Updated WP {uid}"
    assert body["data"]["is_trending"] is True
    assert len(body["data"]["tags"]) == 2

@pytest.mark.asyncio
async def test_delete_wallpaper_admin(client: AsyncClient, admin_headers: dict):
    """Test 12: Admin deletes wallpaper, verifying it can no longer be retrieved."""
    category_id = await get_test_category_id(client)
    uid = uuid.uuid4().hex[:6]

    create_resp = await client.post("/api/v1/wallpapers", json={
        "title": f"To Be Deleted {uid}",
        "category_id": category_id,
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
    wp_id = create_resp.json()["data"]["id"]

    del_resp = await client.delete(f"/api/v1/wallpapers/{wp_id}", headers=admin_headers)
    assert del_resp.status_code == status.HTTP_200_OK
    assert del_resp.json()["data"]["deleted"] is True

    get_resp = await client.get(f"/api/v1/wallpapers/{wp_id}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND
