import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SubscriptionPlan, SubscriptionStatus
from app.models.category import Category
from app.models.wallpaper import Wallpaper

@pytest.fixture
async def sample_wallpaper(db_session: AsyncSession):
    cat = Category(
        name="Monetization Test Cat",
        slug=f"monetization-cat-{uuid.uuid4().hex[:6]}",
        description="Testing category",
    )
    db_session.add(cat)
    await db_session.flush()

    wp = Wallpaper(
        title="8K Ultra Neon Cyberpunk",
        slug=f"8k-ultra-neon-{uuid.uuid4().hex[:6]}",
        category_id=cat.id,
        original_url="https://storage.w8k.app/wallpapers/original.jpg",
        image_url="https://storage.w8k.app/wallpapers/image.jpg",
        thumbnail_url="https://storage.w8k.app/wallpapers/thumb.jpg",
        preview_url="https://storage.w8k.app/wallpapers/preview.jpg",
        width=7680,
        height=4320,
        aspect_ratio=round(7680 / 4320, 4),
        file_size=25000000,
        file_format="JPEG",
        resolution="8K UHD",
        is_premium=True,
        is_published=True,
    )
    db_session.add(wp)
    await db_session.commit()
    await db_session.refresh(wp)
    return wp

@pytest.mark.asyncio
async def test_get_subscription_plans(client: AsyncClient):
    """Test public endpoint returning subscription tiers."""
    response = await client.get("/api/v1/subscriptions/plans")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3
    plan_ids = [p["id"] for p in data["data"]]
    assert "pro_monthly" in plan_ids
    assert "pro_annual" in plan_ids
    assert "pro_lifetime" in plan_ids

@pytest.mark.asyncio
async def test_get_subscription_status_free_user(client: AsyncClient, user_headers: dict):
    """Test initial subscription status for non-subscribed user."""
    response = await client.get("/api/v1/subscriptions/status", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["is_pro"] is False
    assert data["data"]["active_subscription"] is None

@pytest.mark.asyncio
async def test_verify_purchase_and_activate_pro(client: AsyncClient, user_headers: dict):
    """Test purchasing and verifying a Pro monthly subscription."""
    payload = {
        "store": "google_play",
        "product_id": "w8k_pro_monthly",
        "purchase_token": f"gplay_token_{uuid.uuid4().hex}",
        "order_id": f"GPA.1234-5678-{uuid.uuid4().hex[:4]}",
        "plan": SubscriptionPlan.PRO_MONTHLY.value,
    }
    response = await client.post("/api/v1/subscriptions/verify", json=payload, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    sub = data["data"]
    assert sub["plan"] == SubscriptionPlan.PRO_MONTHLY.value
    assert sub["status"] == SubscriptionStatus.ACTIVE.value
    assert sub["auto_renewing"] is True
    assert sub["expires_at"] is not None

    # Check status endpoint now reports Pro
    status_res = await client.get("/api/v1/subscriptions/status", headers=user_headers)
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["data"]["is_pro"] is True
    assert status_data["data"]["plan"] == SubscriptionPlan.PRO_MONTHLY.value

@pytest.mark.asyncio
async def test_verify_purchase_lifetime(client: AsyncClient, user_headers: dict):
    """Test purchasing Lifetime Pro tier has no expiration date."""
    payload = {
        "store": "google_play",
        "product_id": "w8k_pro_lifetime",
        "purchase_token": f"lifetime_token_{uuid.uuid4().hex}",
        "plan": SubscriptionPlan.PRO_LIFETIME.value,
    }
    response = await client.post("/api/v1/subscriptions/verify", json=payload, headers=user_headers)
    assert response.status_code == 200
    sub = response.json()["data"]
    assert sub["plan"] == SubscriptionPlan.PRO_LIFETIME.value
    assert sub["expires_at"] is None
    assert sub["auto_renewing"] is False

@pytest.mark.asyncio
async def test_verify_purchase_invalid_token(client: AsyncClient, user_headers: dict):
    """Test error handling on invalid receipt token."""
    payload = {
        "store": "google_play",
        "product_id": "w8k_pro_monthly",
        "purchase_token": "invalid",
        "plan": SubscriptionPlan.PRO_MONTHLY.value,
    }
    response = await client.post("/api/v1/subscriptions/verify", json=payload, headers=user_headers)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_cancel_subscription(client: AsyncClient, user_headers: dict):
    """Test cancelling subscription auto-renewal."""
    # First activate
    token = f"cancel_test_token_{uuid.uuid4().hex}"
    payload = {
        "store": "google_play",
        "product_id": "w8k_pro_monthly",
        "purchase_token": token,
        "plan": SubscriptionPlan.PRO_MONTHLY.value,
    }
    await client.post("/api/v1/subscriptions/verify", json=payload, headers=user_headers)

    # Cancel
    cancel_res = await client.post(
        "/api/v1/subscriptions/cancel",
        json={"reason": "Testing cancellation"},
        headers=user_headers,
    )
    assert cancel_res.status_code == 200
    sub = cancel_res.json()["data"]
    assert sub["auto_renewing"] is False

@pytest.mark.asyncio
async def test_ad_reward_claim_and_entitlements(
    client: AsyncClient, sample_wallpaper: Wallpaper, user_headers: dict
):
    """Test claiming rewarded ad unlock grants 24-hour access to premium wallpaper."""
    wp_id = str(sample_wallpaper.id)
    tx_id = f"admob_reward_tx_{uuid.uuid4().hex}"

    # Before unlock: free user does not have 8k entitlement for premium wallpaper
    ent_before = await client.get(
        f"/api/v1/monetization/entitlements?wallpaper_id={wp_id}",
        headers=user_headers,
    )
    assert ent_before.status_code == 200
    assert ent_before.json()["data"]["can_download_8k"] is False
    assert ent_before.json()["data"]["has_ad_unlock"] is False

    # Claim ad reward
    claim_payload = {
        "wallpaper_id": wp_id,
        "transaction_id": tx_id,
        "reward_type": "wallpaper_download",
        "ad_network": "admob",
    }
    claim_res = await client.post(
        "/api/v1/monetization/ad-reward",
        json=claim_payload,
        headers=user_headers,
    )
    assert claim_res.status_code == 200
    claim_data = claim_res.json()["data"]
    assert claim_data["unlocked"] is True
    assert claim_data["wallpaper_id"] == wp_id

    # After unlock: user has entitlement
    ent_after = await client.get(
        f"/api/v1/monetization/entitlements?wallpaper_id={wp_id}",
        headers=user_headers,
    )
    assert ent_after.status_code == 200
    assert ent_after.json()["data"]["can_download_8k"] is True
    assert ent_after.json()["data"]["has_ad_unlock"] is True

@pytest.mark.asyncio
async def test_admin_monetization_metrics(
    client: AsyncClient, admin_headers: dict, user_headers: dict
):
    """Test admin monetization metrics endpoint with authorization check."""
    # Forbidden for standard user
    user_res = await client.get("/api/v1/monetization/admin/metrics", headers=user_headers)
    assert user_res.status_code == 403

    # Authorized for admin
    admin_res = await client.get("/api/v1/monetization/admin/metrics", headers=admin_headers)
    assert admin_res.status_code == 200
    data = admin_res.json()["data"]
    assert "active_subscribers" in data
    assert "mrr" in data
    assert "total_revenue" in data
    assert "plan_breakdown" in data

@pytest.mark.asyncio
async def test_admin_subscribers_ledger(
    client: AsyncClient, admin_headers: dict, user_headers: dict
):
    """Test admin subscribers paginated ledger with authorization check."""
    # Forbidden for standard user
    user_res = await client.get("/api/v1/monetization/admin/subscribers", headers=user_headers)
    assert user_res.status_code == 403

    # Authorized for admin
    admin_res = await client.get("/api/v1/monetization/admin/subscribers", headers=admin_headers)
    assert admin_res.status_code == 200
    body = admin_res.json()
    assert body["success"] is True
    assert "data" in body
    assert "meta" in body
    assert body["meta"]["page"] == 1
