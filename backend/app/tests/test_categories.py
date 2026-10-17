import uuid
import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.wallpaper import Wallpaper

@pytest.mark.asyncio
async def test_list_categories(client: AsyncClient):
    """Test 1: GET /api/v1/categories lists active categories with wallpaper counts."""
    response = await client.get("/api/v1/categories")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 10  # Seeded categories
    # Check item schema
    cat = body["data"][0]
    assert "id" in cat
    assert "name" in cat
    assert "slug" in cat
    assert "wallpaper_count" in cat
    assert "sort_order" in cat

@pytest.mark.asyncio
async def test_get_category_by_slug_success(client: AsyncClient):
    """Test 2: GET /api/v1/categories/{slug} returns category details."""
    response = await client.get("/api/v1/categories/nature")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    assert body["data"]["slug"] == "nature"
    assert body["data"]["name"] == "Nature"

@pytest.mark.asyncio
async def test_get_category_not_found(client: AsyncClient):
    """Test 3: GET /api/v1/categories/{slug} with non-existent slug returns 404."""
    response = await client.get("/api/v1/categories/nonexistent-category-slug-xyz")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "CATEGORY_NOT_FOUND"

@pytest.mark.asyncio
async def test_create_category_admin_success(client: AsyncClient, admin_headers: dict):
    """Test 4: POST /api/v1/categories creates category with admin authorization."""
    uid = uuid.uuid4().hex[:6]
    payload = {
        "name": f"Cyberpunk Tech {uid}",
        "description": "High tech and low life wallpapers",
        "sort_order": 99,
        "is_active": True
    }
    response = await client.post("/api/v1/categories", json=payload, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["success"] is True
    assert body["data"]["name"] == payload["name"]
    assert f"cyberpunk-tech-{uid}" in body["data"]["slug"]

@pytest.mark.asyncio
async def test_create_category_forbidden_for_regular_user(client: AsyncClient, user_headers: dict):
    """Test 5: POST /api/v1/categories returns 403 Forbidden for non-admin user."""
    payload = {
        "name": "Hacker Category",
        "description": "Attempt to create without admin permissions"
    }
    response = await client.post("/api/v1/categories", json=payload, headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FORBIDDEN_ROLE"

@pytest.mark.asyncio
async def test_create_category_unauthenticated(client: AsyncClient):
    """Test 6: POST /api/v1/categories without token returns 401 NOT_AUTHENTICATED."""
    payload = {"name": "Anon Category"}
    response = await client.post("/api/v1/categories", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_update_category_admin(client: AsyncClient, admin_headers: dict):
    """Test 7: PUT /api/v1/categories/{id} updates existing category."""
    # Create category first
    uid = uuid.uuid4().hex[:6]
    create_resp = await client.post(
        "/api/v1/categories",
        json={"name": f"Initial Cat {uid}"},
        headers=admin_headers
    )
    cat_id = create_resp.json()["data"]["id"]

    # Update category
    update_resp = await client.put(
        f"/api/v1/categories/{cat_id}",
        json={"description": "Updated description by admin", "sort_order": 5},
        headers=admin_headers
    )
    assert update_resp.status_code == status.HTTP_200_OK
    body = update_resp.json()
    assert body["data"]["description"] == "Updated description by admin"
    assert body["data"]["sort_order"] == 5

@pytest.mark.asyncio
async def test_delete_empty_category_admin(client: AsyncClient, admin_headers: dict):
    """Test 8: DELETE /api/v1/categories/{id} successfully deletes an empty category."""
    uid = uuid.uuid4().hex[:6]
    create_resp = await client.post(
        "/api/v1/categories",
        json={"name": f"Deletable {uid}"},
        headers=admin_headers
    )
    cat_id = create_resp.json()["data"]["id"]

    del_resp = await client.delete(f"/api/v1/categories/{cat_id}", headers=admin_headers)
    assert del_resp.status_code == status.HTTP_200_OK
    assert del_resp.json()["data"]["deleted"] is True

    # Verify not found now
    get_resp = await client.get(f"/api/v1/categories/deletable-{uid}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_category_with_wallpapers_blocked(
    client: AsyncClient,
    admin_headers: dict,
    db_session: AsyncSession
):
    """Test 9: Attempting to delete a category containing wallpapers returns 409 Conflict."""
    uid = uuid.uuid4().hex[:6]
    create_resp = await client.post(
        "/api/v1/categories",
        json={"name": f"Protected Cat {uid}"},
        headers=admin_headers
    )
    cat_id = uuid.UUID(create_resp.json()["data"]["id"])

    # Create wallpaper in this category directly
    wp = Wallpaper(
        title=f"Sample WP {uid}",
        slug=f"sample-wp-{uid}",
        category_id=cat_id,
        original_url="https://storage.wallpapers8k1.com/wp1.png",
        image_url="https://storage.wallpapers8k1.com/wp1.webp",
        thumbnail_url="https://storage.wallpapers8k1.com/wp1_thumb.webp",
        preview_url="https://storage.wallpapers8k1.com/wp1_prev.webp",
        width=7680,
        height=4320,
        aspect_ratio=1.7778,
        file_size=15420000,
        file_format="webp",
        resolution="8K",
        is_published=True
    )
    db_session.add(wp)
    await db_session.commit()

    # Attempt delete
    del_resp = await client.delete(f"/api/v1/categories/{cat_id}", headers=admin_headers)
    assert del_resp.status_code == status.HTTP_409_CONFLICT
    body = del_resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "CATEGORY_NOT_EMPTY"
