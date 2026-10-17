"""
End-to-End Admin Dashboard Flow Verification for Wallpapers_8k1 (W8K1)
Simulates Admin Web Panel API interactions against the live FastAPI Backend.
"""
import sys
import httpx

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@wallpapers8k1.com"
ADMIN_PASSWORD = "AdminSecurePassword123!"

results = []

def record(test_name: str, passed: bool, details: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {test_name}: {details}")
    results.append((test_name, passed, details))

def main():
    print("=" * 70)
    print("  WALLPAPERS_8K1 — ADMIN DASHBOARD WORKFLOW VERIFICATION")
    print("=" * 70)

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Admin Authentication
        token = None
        try:
            r = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
            data = r.json()
            if r.status_code == 200 and data.get("success"):
                token = data["data"]["access_token"]
                user = data["data"]["user"]
                record("1. Admin Authentication", user.get("role") in ("ADMIN", "SUPER_ADMIN"), f"Role: {user.get('role')}, Email: {user.get('email')}")
            else:
                record("1. Admin Authentication", False, f"HTTP {r.status_code}: {data}")
        except Exception as e:
            record("1. Admin Authentication", False, str(e))

        if not token:
            print("Fatal: Cannot continue without admin token.")
            sys.exit(1)

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Dashboard KPI Metrics
        try:
            r = client.get("/admin/dashboard", headers=headers)
            data = r.json()
            metrics = data.get("data", {})
            record("2. Dashboard Metrics", r.status_code == 200 and data.get("success"), 
                   f"Wallpapers: {metrics.get('total_wallpapers')}, Users: {metrics.get('total_users')}, Downloads: {metrics.get('total_downloads')}")
        except Exception as e:
            record("2. Dashboard Metrics", False, str(e))

        # 3. Wallpaper Management Grid
        try:
            r = client.get("/admin/wallpapers?page=1&limit=10", headers=headers)
            data = r.json()
            items = data.get("data", [])
            meta = data.get("meta", {})
            record("3. Wallpaper Grid Listing", r.status_code == 200 and len(items) > 0, 
                   f"Loaded {len(items)} items, Page 1 of {meta.get('total_pages')}, Total: {meta.get('total')}")
        except Exception as e:
            record("3. Wallpaper Grid Listing", False, str(e))

        # 4. Category Management
        try:
            r = client.get("/categories", headers=headers)
            data = r.json()
            cats = data.get("data", [])
            record("4. Category Management Listing", r.status_code == 200 and len(cats) > 0, 
                   f"Active categories: {len(cats)}")
        except Exception as e:
            record("4. Category Management Listing", False, str(e))

        # 5. Content Moderation Reports
        try:
            r = client.get("/admin/reports?page=1&limit=10", headers=headers)
            data = r.json()
            reps = data.get("data", [])
            record("5. Moderation Reports Queue", r.status_code == 200, f"Pending/resolved reports: {len(reps)}")
        except Exception as e:
            record("5. Moderation Reports Queue", False, str(e))

        # 6. Monetization & Subscriptions Metrics
        try:
            r = client.get("/monetization/admin/metrics", headers=headers)
            data = r.json()
            m_data = data.get("data", {})
            record("6. Monetization Metrics", r.status_code == 200 and data.get("success"), 
                   f"VIP Subscribers: {m_data.get('total_subscribers')}, Ad Unlocks Today: {m_data.get('ad_rewards_today')}")
        except Exception as e:
            record("6. Monetization Metrics", False, str(e))

        # 7. AI Search Analytics & Color Distribution
        try:
            r = client.get("/search/analytics", headers=headers)
            data = r.json()
            s_data = data.get("data", {})
            record("7. AI Search Analytics", r.status_code == 200 and data.get("success"), 
                   f"Coverage: {s_data.get('ai_coverage_percentage')}%, Unique Colors: {len(s_data.get('dominant_color_distribution', []))}")
        except Exception as e:
            record("7. AI Search Analytics", False, str(e))

    print("=" * 70)
    passed_count = sum(1 for _, p, _ in results if p)
    print(f"Summary: {passed_count}/{len(results)} Admin Dashboard flows PASSED.")
    print("=" * 70)
    if passed_count != len(results):
        sys.exit(1)

if __name__ == "__main__":
    main()
