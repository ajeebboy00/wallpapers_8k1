import uuid
import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.constants import ReportReason, ReportStatus, UserRole

async def create_test_wallpaper(client: AsyncClient, admin_headers: dict, title: str = "Admin Test Wallpaper") -> dict:
    cat_resp = await client.get("/api/v1/categories")
    category_id = cat_resp.json()["data"][0]["id"]
    uid = uuid.uuid4().hex[:6]
    payload = {
        "title": f"{title} {uid}",
        "description": "8K Admin wallpaper test",
        "category_id": category_id,
        "original_url": f"https://storage.wallpapers8k1.com/raw/{uid}.png",
        "image_url": f"https://storage.wallpapers8k1.com/opt/{uid}.webp",
        "thumbnail_url": f"https://storage.wallpapers8k1.com/thumb/{uid}.webp",
        "preview_url": f"https://storage.wallpapers8k1.com/prev/{uid}.webp",
        "width": 7680,
        "height": 4320,
        "file_size": 28000000,
        "file_format": "webp",
        "resolution": "8K",
        "is_published": True,
        "tags": ["admin", "test"]
    }
    resp = await client.post("/api/v1/wallpapers", json=payload, headers=admin_headers)
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.json()["data"]

@pytest.mark.asyncio
async def test_admin_dashboard_metrics(client: AsyncClient, user_headers: dict, admin_headers: dict):
    """Test 1: Access control and comprehensive dashboard KPI data retrieval."""
    # 1. Non-admin access should be forbidden (403)
    forbidden_resp = await client.get("/api/v1/admin/dashboard", headers=user_headers)
    assert forbidden_resp.status_code == status.HTTP_403_FORBIDDEN

    # 2. Admin access should succeed with full KPIs
    resp = await client.get("/api/v1/admin/dashboard", headers=admin_headers)
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    data = body["data"]

    # Verify all expected KPI fields exist
    assert "total_wallpapers" in data
    assert "total_categories" in data
    assert "total_collections" in data
    assert "total_users" in data
    assert "total_views" in data
    assert "total_downloads" in data
    assert "total_favorites" in data
    assert "total_reports" in data
    assert "storage_used_bytes" in data
    assert "recent_wallpapers" in data
    assert "pending_reports" in data

    assert isinstance(data["recent_wallpapers"], list)
    assert isinstance(data["pending_reports"], list)

@pytest.mark.asyncio
async def test_admin_list_wallpapers_and_filters(client: AsyncClient, admin_headers: dict):
    """Test 2: Administrative wallpaper listing with query filters and pagination."""
    wp = await create_test_wallpaper(client, admin_headers, title="UniqueFilterTarget")

    resp = await client.get(
        f"/api/v1/admin/wallpapers?search=UniqueFilterTarget&page=1&limit=10",
        headers=admin_headers
    )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    items = body["data"]
    assert len(items) >= 1
    assert any(i["id"] == wp["id"] for i in items)
    assert body["meta"]["total"] >= 1

@pytest.mark.asyncio
async def test_admin_toggle_publish_status(client: AsyncClient, admin_headers: dict):
    """Test 3: Unpublish and re-publish wallpaper toggle."""
    wp = await create_test_wallpaper(client, admin_headers)
    wp_id = wp["id"]
    assert wp["is_published"] is True

    # 1. Unpublish
    resp1 = await client.patch(f"/api/v1/admin/wallpapers/{wp_id}/publish", headers=admin_headers)
    assert resp1.status_code == status.HTTP_200_OK
    assert resp1.json()["data"]["is_published"] is False

    # 2. Re-publish
    resp2 = await client.patch(f"/api/v1/admin/wallpapers/{wp_id}/publish", headers=admin_headers)
    assert resp2.status_code == status.HTTP_200_OK
    assert resp2.json()["data"]["is_published"] is True

@pytest.mark.asyncio
async def test_admin_toggle_featured_and_daily(client: AsyncClient, admin_headers: dict):
    """Test 4: Toggle featured state and assign daily spotlight."""
    wp = await create_test_wallpaper(client, admin_headers)
    wp_id = wp["id"]

    # 1. Feature
    resp_feat = await client.patch(f"/api/v1/admin/wallpapers/{wp_id}/feature", headers=admin_headers)
    assert resp_feat.status_code == status.HTTP_200_OK
    assert resp_feat.json()["data"]["is_featured"] is True

    # 2. Daily Spotlight
    resp_daily = await client.patch(f"/api/v1/admin/wallpapers/{wp_id}/daily", headers=admin_headers)
    assert resp_daily.status_code == status.HTTP_200_OK
    assert resp_daily.json()["data"]["is_daily"] is True

@pytest.mark.asyncio
async def test_admin_delete_wallpaper(client: AsyncClient, admin_headers: dict):
    """Test 5: Permanently delete wallpaper via administrative endpoint."""
    wp = await create_test_wallpaper(client, admin_headers)
    wp_id = wp["id"]

    resp = await client.delete(f"/api/v1/admin/wallpapers/{wp_id}", headers=admin_headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["deleted"] is True

    # Confirm it cannot be fetched
    get_resp = await client.get(f"/api/v1/wallpapers/{wp_id}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_admin_user_management_and_role_escalation(
    client: AsyncClient,
    regular_user,
    admin_headers: dict,
    super_admin_headers: dict
):
    """Test 6: User status toggling and RBAC role assignment."""
    user_id = str(regular_user.id)

    # 1. List users
    resp_list = await client.get("/api/v1/admin/users?limit=10", headers=admin_headers)
    assert resp_list.status_code == status.HTTP_200_OK
    assert resp_list.json()["meta"]["total"] >= 1

    # 2. Deactivate user
    resp_deact = await client.patch(
        f"/api/v1/admin/users/{user_id}/status",
        json={"is_active": False},
        headers=admin_headers
    )
    assert resp_deact.status_code == status.HTTP_200_OK
    assert resp_deact.json()["data"]["is_active"] is False

    # 3. Reactivate user
    resp_act = await client.patch(
        f"/api/v1/admin/users/{user_id}/status",
        json={"is_active": True},
        headers=admin_headers
    )
    assert resp_act.status_code == status.HTTP_200_OK
    assert resp_act.json()["data"]["is_active"] is True

    # 4. Standard Admin cannot change roles (Requires SUPER_ADMIN)
    resp_role_forbidden = await client.patch(
        f"/api/v1/admin/users/{user_id}/role",
        json={"role": UserRole.ADMIN.value},
        headers=admin_headers
    )
    assert resp_role_forbidden.status_code == status.HTTP_403_FORBIDDEN

    # 5. Super Admin changes role
    resp_role_ok = await client.patch(
        f"/api/v1/admin/users/{user_id}/role",
        json={"role": UserRole.ADMIN.value},
        headers=super_admin_headers
    )
    assert resp_role_ok.status_code == status.HTTP_200_OK
    assert resp_role_ok.json()["data"]["role"] == UserRole.ADMIN.value

@pytest.mark.asyncio
async def test_admin_moderation_queue_and_resolve(
    client: AsyncClient,
    user_headers: dict,
    admin_headers: dict
):
    """Test 7: Moderation queue listing and resolution with automatic unpublishing."""
    wp = await create_test_wallpaper(client, admin_headers)
    wp_id = wp["id"]

    # 1. File a report
    rep_resp = await client.post(
        f"/api/v1/wallpapers/{wp_id}/report",
        json={"reason": ReportReason.INAPPROPRIATE.value, "description": "Violates guidelines"},
        headers=user_headers
    )
    assert rep_resp.status_code == status.HTTP_201_CREATED
    rep_id = rep_resp.json()["data"]["id"]

    # 2. Admin retrieves reports queue
    queue_resp = await client.get("/api/v1/admin/reports?status=PENDING", headers=admin_headers)
    assert queue_resp.status_code == status.HTTP_200_OK
    reports = queue_resp.json()["data"]
    assert any(r["id"] == rep_id for r in reports)

    # 3. Resolve report with unpublish_wallpaper=True
    resolve_resp = await client.patch(
        f"/api/v1/admin/reports/{rep_id}/resolve",
        json={
            "status": ReportStatus.RESOLVED.value,
            "unpublish_wallpaper": True
        },
        headers=admin_headers
    )
    assert resolve_resp.status_code == status.HTTP_200_OK
    res_data = resolve_resp.json()["data"]
    assert res_data["status"] == ReportStatus.RESOLVED.value

    # 4. Verify wallpaper was actually unpublished
    wp_check = await client.get(f"/api/v1/wallpapers/{wp_id}")
    if wp_check.status_code == status.HTTP_200_OK:
        assert wp_check.json()["data"]["is_published"] is False

@pytest.mark.asyncio
async def test_admin_analytics_timeseries(client: AsyncClient, admin_headers: dict):
    """Test 8: Aggregated 7-day administrative engagement analytics."""
    resp = await client.get("/api/v1/admin/analytics?days=7", headers=admin_headers)
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["success"] is True
    points = body["data"]
    assert len(points) == 7
    for pt in points:
        assert "date" in pt
        assert "views" in pt
        assert "downloads" in pt
        assert "favorites" in pt
