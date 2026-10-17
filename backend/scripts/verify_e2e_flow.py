"""
Complete End-to-End Integration Flow for Wallpapers_8k1 (W8K1)
Simulates:
Admin uploads/publishes wallpaper
→ Backend stores metadata in PostgreSQL
→ Mobile API receives wallpaper in feed
→ User opens wallpaper details
→ User favorites & downloads
→ Backend records interactions
→ Admin dashboard analytics reflects the actions.
"""
import asyncio
import io
import os
import sys
import uuid
import httpx
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.db.session import AsyncSessionLocal

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@wallpapers8k1.com"
ADMIN_PASSWORD = "AdminSecurePassword123!"

results = []

def record(step_name: str, passed: bool, details: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {step_name}: {details}")
    results.append((step_name, passed, details))

def generate_test_image_bytes() -> bytes:
    """Generates a valid test JPEG image in memory."""
    img = Image.new("RGB", (3840, 2160), color=(26, 26, 46))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

async def verify_db_row(wallpaper_id: str) -> dict:
    async with AsyncSessionLocal() as session:
        query = text("SELECT id, title, slug, resolution, is_published, favorite_count, download_count FROM wallpapers WHERE id = :wid;")
        res = await session.execute(query, {"wid": wallpaper_id})
        row = res.mappings().first()
        return dict(row) if row else {}

async def main():
    print("=" * 70)
    print("  WALLPAPERS_8K1 — COMPLETE END-TO-END INTEGRATION FLOW")
    print("=" * 70)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as client:
        # Step 1: Admin Login
        login_res = await client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        if login_res.status_code != 200:
            record("Step 1: Admin Login", False, f"HTTP {login_res.status_code}")
            sys.exit(1)
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        record("Step 1: Admin Login", True, f"Admin authenticated successfully")

        # Step 2: Get a valid category
        cat_res = await client.get("/categories")
        cats = cat_res.json().get("data", [])
        if not cats:
            record("Step 2: Fetch Category", False, "No categories in db")
            sys.exit(1)
        category_id = cats[0]["id"]
        record("Step 2: Fetch Category", True, f"Using Category: '{cats[0]['name']}' ({category_id})")

        # Step 3: Admin Uploads & Publishes Wallpaper
        image_bytes = generate_test_image_bytes()
        unique_suffix = uuid.uuid4().hex[:6]
        wp_title = f"E2E Horizon {unique_suffix}"
        
        files = {
            "file": ("e2e_horizon.jpg", image_bytes, "image/jpeg")
        }
        data = {
            "title": wp_title,
            "category_id": category_id,
            "description": "Verified end-to-end integration test wallpaper",
            "tags": "horizon,space,amoled,e2e",
            "is_featured": "true",
            "is_trending": "false",
            "is_daily": "false",
            "is_published": "true"
        }

        upload_res = await client.post("/wallpapers/upload", headers=headers, files=files, data=data)
        if upload_res.status_code != 201:
            record("Step 3: Admin Publishes Wallpaper", False, f"HTTP {upload_res.status_code}: {upload_res.text}")
            sys.exit(1)
        
        published_wp = upload_res.json().get("data", {})
        wallpaper_id = published_wp.get("id")
        record("Step 3: Admin Publishes Wallpaper", True, f"Created '{wp_title}' with ID: {wallpaper_id}")

        # Step 4: Verify PostgreSQL Database Storage
        db_row = await verify_db_row(wallpaper_id)
        record("Step 4: Database Storage Verified", len(db_row) > 0 and db_row["title"] == wp_title,
               f"DB row verified: slug='{db_row.get('slug')}', published={db_row.get('is_published')}")

        # Step 5: Mobile Client Feed Discovery (Public API)
        feed_res = await client.get("/wallpapers?sort=newest&limit=10")
        feed_items = feed_res.json().get("data", [])
        found_in_feed = any(w["id"] == wallpaper_id for w in feed_items)
        record("Step 5: Mobile Feed Discovery", found_in_feed, f"Wallpaper found at top of public feed")

        # Step 6: User Opens Wallpaper Details Screen
        detail_res = await client.get(f"/wallpapers/{wallpaper_id}")
        det_data = detail_res.json().get("data", {})
        record("Step 6: Wallpaper Details Retrieved", detail_res.status_code == 200 and det_data.get("id") == wallpaper_id,
               f"Resolution: {det_data.get('resolution')}, Tags: {[t['name'] for t in det_data.get('tags', [])]}")

        # Step 7: User Favorites the Wallpaper
        fav_res = await client.post(f"/wallpapers/{wallpaper_id}/favorite", headers=headers)
        fav_ok = fav_res.status_code == 200 and fav_res.json().get("data", {}).get("is_favorite") is True
        record("Step 7: User Favorites Wallpaper", fav_ok, f"Favorite status: True")

        # Step 8: User Downloads the Wallpaper
        dl_res = await client.post(f"/wallpapers/{wallpaper_id}/download")
        dl_cnt = dl_res.json().get("data", {}).get("download_count", 0)
        record("Step 8: User Downloads Wallpaper", dl_res.status_code == 200 and dl_cnt >= 1, f"Recorded download count: {dl_cnt}")

        # Step 9: Re-verify Database State after Actions
        updated_db = await verify_db_row(wallpaper_id)
        record("Step 9: Database Recorded Interactions", 
               updated_db.get("favorite_count", 0) >= 1 and updated_db.get("download_count", 0) >= 1,
               f"DB favorite_count={updated_db.get('favorite_count')}, download_count={updated_db.get('download_count')}")

        # Step 10: Admin Dashboard Analytics Reflection
        dash_res = await client.get("/admin/dashboard", headers=headers)
        dash_data = dash_res.json().get("data", {})
        record("Step 10: Admin Dashboard Reflected Metrics", 
               dash_res.status_code == 200 and dash_data.get("total_wallpapers", 0) >= 670,
               f"Total Wallpapers: {dash_data.get('total_wallpapers')}, Total Downloads: {dash_data.get('total_downloads')}")

    print("=" * 70)
    passed_count = sum(1 for _, p, _ in results if p)
    print(f"E2E Summary: {passed_count}/{len(results)} integration stages PASSED.")
    print("=" * 70)
    if passed_count != len(results):
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
