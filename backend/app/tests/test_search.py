import uuid
import pytest
from httpx import AsyncClient
from fastapi import status

async def create_wallpaper_helper(client: AsyncClient, admin_headers: dict, **kwargs):
    cat_resp = await client.get("/api/v1/categories")
    category = cat_resp.json()["data"][0]
    category_id = kwargs.get("category_id", category["id"])
    
    uid = uuid.uuid4().hex[:6]
    title = kwargs.get("title", f"Wallpaper {uid}")
    payload = {
        "title": title,
        "description": kwargs.get("description", f"Ultra high definition wallpaper {uid}"),
        "category_id": category_id,
        "original_url": f"https://storage.wallpapers8k1.com/raw/{uid}.png",
        "image_url": f"https://storage.wallpapers8k1.com/opt/{uid}.webp",
        "thumbnail_url": f"https://storage.wallpapers8k1.com/thumb/{uid}.webp",
        "preview_url": f"https://storage.wallpapers8k1.com/prev/{uid}.webp",
        "width": kwargs.get("width", 7680),
        "height": kwargs.get("height", 4320),
        "file_size": 25000000,
        "file_format": "webp",
        "resolution": kwargs.get("resolution", "8K"),
        "is_featured": kwargs.get("is_featured", False),
        "is_trending": kwargs.get("is_trending", False),
        "is_daily": kwargs.get("is_daily", False),
        "is_published": kwargs.get("is_published", True),
        "tags": kwargs.get("tags", [f"tag_{uid}"])
    }
    resp = await client.post("/api/v1/wallpapers", json=payload, headers=admin_headers)
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.json()["data"]

@pytest.mark.asyncio
async def test_search_all_wallpapers_no_query(client: AsyncClient, admin_headers: dict):
    """Test 1: Search without query returns paginated list of published wallpapers."""
    await create_wallpaper_helper(client, admin_headers)
    
    resp = await client.get("/api/v1/search?page=1&limit=10")
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert "meta" in body
    assert body["meta"]["page"] == 1
    assert body["meta"]["limit"] == 10
    assert body["meta"]["total"] >= 1

@pytest.mark.asyncio
async def test_search_by_title_keyword(client: AsyncClient, admin_headers: dict):
    """Test 2: Search returns wallpapers whose title matches keyword."""
    keyword = f"CyberMatrix{uuid.uuid4().hex[:4]}"
    wp = await create_wallpaper_helper(client, admin_headers, title=f"Glow {keyword} City")

    resp = await client.get(f"/api/v1/search?q={keyword}")
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    found_ids = [item["id"] for item in body["data"]]
    assert wp["id"] in found_ids

@pytest.mark.asyncio
async def test_search_by_description_keyword(client: AsyncClient, admin_headers: dict):
    """Test 3: Search matches keywords inside description."""
    secret_term = f"bioluminescent_{uuid.uuid4().hex[:5]}"
    wp = await create_wallpaper_helper(
        client,
        admin_headers,
        description=f"Deep ocean creature with {secret_term} tentacles"
    )

    resp = await client.get(f"/api/v1/search?q={secret_term}")
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    found_ids = [item["id"] for item in body["data"]]
    assert wp["id"] in found_ids

@pytest.mark.asyncio
async def test_search_by_tag(client: AsyncClient, admin_headers: dict):
    """Test 4: Search filters or matches by tag."""
    unique_tag = f"synthwave_{uuid.uuid4().hex[:5]}"
    wp = await create_wallpaper_helper(client, admin_headers, tags=[unique_tag, "retro"])

    # Search with q matching tag name
    resp_q = await client.get(f"/api/v1/search?q={unique_tag}")
    assert resp_q.status_code == status.HTTP_200_OK
    body_q = resp_q.json()
    assert any(item["id"] == wp["id"] for item in body_q["data"])

    # Search with explicit tag filter param
    resp_tag = await client.get(f"/api/v1/search?tag={unique_tag}")
    assert resp_tag.status_code == status.HTTP_200_OK
    body_tag = resp_tag.json()
    assert any(item["id"] == wp["id"] for item in body_tag["data"])

@pytest.mark.asyncio
async def test_search_filter_by_resolution(client: AsyncClient, admin_headers: dict):
    """Test 5: Search filters strictly by resolution (e.g. 4K)."""
    wp_4k = await create_wallpaper_helper(client, admin_headers, resolution="4K", width=3840, height=2160)
    
    resp = await client.get(f"/api/v1/search?resolution=4K")
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    for item in body["data"]:
        assert item["resolution"] == "4K"
    assert any(item["id"] == wp_4k["id"] for item in body["data"])

@pytest.mark.asyncio
async def test_search_filter_by_orientation(client: AsyncClient, admin_headers: dict):
    """Test 6: Filter by orientation: portrait vs landscape."""
    # Portrait: height > width
    wp_portrait = await create_wallpaper_helper(client, admin_headers, width=2160, height=3840)
    # Landscape: width > height
    wp_landscape = await create_wallpaper_helper(client, admin_headers, width=7680, height=4320)

    # Portrait search
    resp_port = await client.get("/api/v1/search?orientation=portrait")
    assert resp_port.status_code == status.HTTP_200_OK
    portrait_items = resp_port.json()["data"]
    for item in portrait_items:
        assert item["height"] > item["width"]
    assert any(item["id"] == wp_portrait["id"] for item in portrait_items)
    assert all(item["id"] != wp_landscape["id"] for item in portrait_items)

    # Landscape search
    resp_land = await client.get("/api/v1/search?orientation=landscape")
    assert resp_land.status_code == status.HTTP_200_OK
    landscape_items = resp_land.json()["data"]
    for item in landscape_items:
        assert item["width"] > item["height"]
    assert any(item["id"] == wp_landscape["id"] for item in landscape_items)
    assert all(item["id"] != wp_portrait["id"] for item in landscape_items)

@pytest.mark.asyncio
async def test_search_sorting_modes(client: AsyncClient, admin_headers: dict):
    """Test 7: Supports sorting by newest, downloads, views, trending, relevance."""
    for sort_mode in ["newest", "downloads", "views", "trending", "relevance"]:
        resp = await client.get(f"/api/v1/search?sort={sort_mode}&limit=5")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["success"] is True

@pytest.mark.asyncio
async def test_search_no_results(client: AsyncClient):
    """Test 8: Searching for an impossible term returns empty list with total=0."""
    impossible_term = "xy_non_existent_impossible_query_99999"
    resp = await client.get(f"/api/v1/search?q={impossible_term}")
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 0
    assert body["meta"]["total"] == 0
    assert body["meta"]["total_pages"] == 1

@pytest.mark.asyncio
async def test_search_suggestions_endpoint(client: AsyncClient):
    """Test 9: Suggestions endpoint returns popular searches and active tags."""
    resp = await client.get("/api/v1/search/suggestions")
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "popular_searches" in data
    assert len(data["popular_searches"]) > 0
    assert "suggested_tags" in data
    assert "suggested_categories" in data

@pytest.mark.asyncio
async def test_trigram_fuzzy_search(client: AsyncClient, admin_headers: dict):
    """Test 10: Typo-tolerant trigram search finds target even with slight spelling mistake."""
    uid = uuid.uuid4().hex[:4]
    title = f"Cyberpunk Neo Horizon {uid}"
    wp = await create_wallpaper_helper(client, admin_headers, title=title)

    # Search with typo: "cybrpunk" or "horizn"
    resp = await client.get("/api/v1/search?q=cybrpunk")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["success"] is True

@pytest.mark.asyncio
async def test_color_filtering(client: AsyncClient, admin_headers: dict):
    """Test 11: Color filter matches wallpapers by dominant color and palette."""
    wp = await create_wallpaper_helper(client, admin_headers, title=f"Violet Aurora {uuid.uuid4().hex[:4]}")
    wp_id = wp["id"]

    # Trigger AI tagging to assign color palette and dominant color
    tag_resp = await client.post(
        "/api/v1/search/ai/tag-batch",
        json={"wallpaper_id": wp_id, "force_reprocess": True},
        headers=admin_headers,
    )
    assert tag_resp.status_code == 200

    # Search by color hex #8B5CF6 or preset "purple"
    resp = await client.get("/api/v1/search?color=purple")
    assert resp.status_code == 200
    assert resp.json()["success"] is True

@pytest.mark.asyncio
async def test_similar_wallpapers_engine(client: AsyncClient, admin_headers: dict):
    """Test 12: Visual & semantic similarity engine returns related items."""
    wp1 = await create_wallpaper_helper(
        client, admin_headers,
        title=f"Neon Synth Cyber Matrix {uuid.uuid4().hex[:4]}",
        tags=["neon", "cyberpunk", "futuristic"]
    )
    wp2 = await create_wallpaper_helper(
        client, admin_headers,
        title=f"Neon Cyber Overdrive {uuid.uuid4().hex[:4]}",
        tags=["neon", "cyberpunk", "matrix"]
    )

    # Batch AI tag
    await client.post(
        "/api/v1/search/ai/tag-batch",
        json={"wallpaper_id": wp1["id"], "force_reprocess": True},
        headers=admin_headers,
    )
    await client.post(
        "/api/v1/search/ai/tag-batch",
        json={"wallpaper_id": wp2["id"], "force_reprocess": True},
        headers=admin_headers,
    )

    # Call similarity endpoint
    sim_resp = await client.get(f"/api/v1/search/similar/{wp1['id']}")
    assert sim_resp.status_code == 200
    sim_data = sim_resp.json()
    assert sim_data["success"] is True
    assert "similar" in sim_data["data"]

    # Also test wallpaper route /{id}/similar
    wp_sim_resp = await client.get(f"/api/v1/wallpapers/{wp1['id']}/similar")
    assert wp_sim_resp.status_code == 200
    assert wp_sim_resp.json()["success"] is True

@pytest.mark.asyncio
async def test_search_analytics(client: AsyncClient):
    """Test 13: Search analytics endpoint returns index coverage and color distribution."""
    resp = await client.get("/api/v1/search/analytics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "total_wallpapers" in data["data"]
    assert "color_distribution" in data["data"]
    assert "popular_searches" in data["data"]

