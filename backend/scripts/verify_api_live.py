"""
Live API Verification Script for Wallpapers_8k1 (W8K1)
Executes real HTTP requests against the live running FastAPI server at http://localhost:8000
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
    print("  WALLPAPERS_8K1 — LIVE API VERIFICATION")
    print("=" * 70)

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Health Checks
        try:
            r = client.get("/health")
            data = r.json()
            record("GET /health", r.status_code == 200 and data.get("success") is True, f"status={data['data']['status']}, db={data['data']['database']}")
        except Exception as e:
            record("GET /health", False, str(e))

        try:
            r = client.get("/health/live")
            record("GET /health/live", r.status_code == 200, f"resp={r.json().get('status')}")
        except Exception as e:
            record("GET /health/live", False, str(e))

        try:
            r = client.get("/health/ready")
            record("GET /health/ready", r.status_code == 200 and r.json().get("success"), f"ready={r.json().get('data', {}).get('ready')}")
        except Exception as e:
            record("GET /health/ready", False, str(e))

        # 2. Authentication
        token = None
        try:
            r = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
            login_data = r.json()
            if r.status_code == 200 and login_data.get("success"):
                token = login_data["data"]["access_token"]
                record("POST /auth/login", True, f"token received, user={login_data['data']['user']['email']}")
            else:
                record("POST /auth/login", False, f"status={r.status_code}, data={login_data}")
        except Exception as e:
            record("POST /auth/login", False, str(e))

        auth_headers = {"Authorization": f"Bearer {token}"} if token else {}

        if token:
            try:
                r = client.get("/auth/me", headers=auth_headers)
                me_data = r.json()
                record("GET /auth/me", r.status_code == 200 and me_data.get("success"), f"role={me_data['data']['role']}")
            except Exception as e:
                record("GET /auth/me", False, str(e))

        # 3. Wallpapers Endpoints
        sample_wallpaper_id = None
        try:
            r = client.get("/wallpapers?page=1&limit=5")
            wall_data = r.json()
            items = wall_data.get("data", []) if isinstance(wall_data.get("data"), list) else []
            total = wall_data.get("meta", {}).get("total", 0)
            if items:
                sample_wallpaper_id = items[0]["id"]
            record("GET /wallpapers", r.status_code == 200 and len(items) > 0, f"fetched {len(items)} items (total {total} in db)")
        except Exception as e:
            record("GET /wallpapers", False, str(e))

        try:
            r = client.get("/wallpapers/daily")
            daily_data = r.json()
            record("GET /wallpapers/daily", r.status_code == 200 and daily_data.get("success"), f"title='{daily_data.get('data', {}).get('title')}'")
        except Exception as e:
            record("GET /wallpapers/daily", False, str(e))

        if sample_wallpaper_id:
            try:
                r = client.get(f"/wallpapers/{sample_wallpaper_id}")
                det_data = r.json()
                record(f"GET /wallpapers/{sample_wallpaper_id[:8]}...", r.status_code == 200 and det_data.get("success"), f"title='{det_data.get('data', {}).get('title')}'")
            except Exception as e:
                record("GET /wallpapers/{id}", False, str(e))

            try:
                r = client.get(f"/wallpapers/{sample_wallpaper_id}/similar?limit=3")
                sim_data = r.json()
                record(f"GET /wallpapers/{sample_wallpaper_id[:8]}.../similar", r.status_code == 200 and sim_data.get("success"), f"found {len(sim_data.get('data', []))} similar")
            except Exception as e:
                record("GET /wallpapers/{id}/similar", False, str(e))

        # 4. Categories Endpoints
        try:
            r = client.get("/categories")
            cat_data = r.json()
            cats = cat_data.get("data", [])
            record("GET /categories", r.status_code == 200 and len(cats) > 0, f"found {len(cats)} active categories")
        except Exception as e:
            record("GET /categories", False, str(e))

        # 5. Collections Endpoints
        try:
            r = client.get("/collections")
            col_data = r.json()
            cols = col_data.get("data", []) if isinstance(col_data.get("data"), list) else []
            record("GET /collections", r.status_code == 200, f"found {len(cols)} collections")
        except Exception as e:
            record("GET /collections", False, str(e))

        # 6. Search Endpoints
        try:
            r = client.get("/search?q=nature&limit=5")
            srch_data = r.json()
            srch_items = srch_data.get("data", []) if isinstance(srch_data.get("data"), list) else []
            record("GET /search?q=nature", r.status_code == 200 and srch_data.get("success"), f"found {len(srch_items)} matches")
        except Exception as e:
            record("GET /search", False, str(e))

        try:
            r = client.get("/search/suggestions?q=a")
            sug_data = r.json()
            record("GET /search/suggestions?q=a", r.status_code == 200 and sug_data.get("success"), f"returned {len(sug_data.get('data', []))} suggestions")
        except Exception as e:
            record("GET /search/suggestions", False, str(e))

        # 7. Interactions: Favorite & Download
        if sample_wallpaper_id and token:
            try:
                r = client.post(f"/wallpapers/{sample_wallpaper_id}/favorite", headers=auth_headers)
                fav_data = r.json()
                record("POST /wallpapers/.../favorite", r.status_code == 200 and fav_data.get("success"), f"is_favorite={fav_data.get('data', {}).get('is_favorite')}")
            except Exception as e:
                record("POST /wallpapers/{id}/favorite", False, str(e))

            try:
                r = client.post(f"/wallpapers/{sample_wallpaper_id}/download")
                dl_data = r.json()
                record("POST /wallpapers/.../download", r.status_code == 200 and dl_data.get("success"), f"count={dl_data.get('data', {}).get('download_count')}")
            except Exception as e:
                record("POST /wallpapers/{id}/download", False, str(e))

        # 8. Notifications
        if token:
            try:
                r = client.get("/notifications", headers=auth_headers)
                notif_data = r.json()
                notifs = notif_data.get("data", []) if isinstance(notif_data.get("data"), list) else []
                record("GET /notifications", r.status_code == 200 and notif_data.get("success"), f"retrieved {len(notifs)} items")
            except Exception as e:
                record("GET /notifications", False, str(e))

            try:
                r = client.get("/notifications/unread-count", headers=auth_headers)
                cnt_data = r.json()
                record("GET /notifications/unread-count", r.status_code == 200 and cnt_data.get("success"), f"unread={cnt_data.get('data', {}).get('unread_count')}")
            except Exception as e:
                record("GET /notifications/unread-count", False, str(e))

            try:
                r = client.get("/users/me/notification-preferences", headers=auth_headers)
                pref_data = r.json()
                record("GET /users/me/notification-preferences", r.status_code == 200 and pref_data.get("success"), "preferences retrieved")
            except Exception as e:
                record("GET /users/me/notification-preferences", False, str(e))

        # 9. Admin Endpoints
        if token:
            try:
                r = client.get("/admin/dashboard", headers=auth_headers)
                dash_data = r.json()
                d_info = dash_data.get("data", {})
                record("GET /admin/dashboard", r.status_code == 200 and dash_data.get("success"), f"total_wallpapers={d_info.get('total_wallpapers')}, total_users={d_info.get('total_users')}")
            except Exception as e:
                record("GET /admin/dashboard", False, str(e))

            try:
                r = client.get("/admin/wallpapers?page=1&limit=5", headers=auth_headers)
                adm_wall = r.json()
                adm_items = adm_wall.get("data", []) if isinstance(adm_wall.get("data"), list) else []
                record("GET /admin/wallpapers", r.status_code == 200 and adm_wall.get("success"), f"items={len(adm_items)}")
            except Exception as e:
                record("GET /admin/wallpapers", False, str(e))

            try:
                r = client.get("/admin/reports", headers=auth_headers)
                rep_data = r.json()
                rep_items = rep_data.get("data", []) if isinstance(rep_data.get("data"), list) else []
                record("GET /admin/reports", r.status_code == 200 and rep_data.get("success"), f"reports={len(rep_items)}")
            except Exception as e:
                record("GET /admin/reports", False, str(e))

    print("=" * 70)
    passed_count = sum(1 for _, p, _ in results if p)
    print(f"Summary: {passed_count}/{len(results)} live API checks PASSED.")
    print("=" * 70)
    if passed_count != len(results):
        sys.exit(1)

if __name__ == "__main__":
    main()
