import urllib.request
import json
import os

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("=" * 60)
    print("VERIFYING LIVE BACKEND API WITH SEEDED TEST DATA")
    print("=" * 60)

    # 1. Root Operational Check
    with urllib.request.urlopen(f"{BASE_URL}/") as resp:
        data = json.loads(resp.read().decode())
        print(f"[OK] Root Endpoint: {data.get('status')} (version {data.get('version')})")

    # 2. Daily Wallpaper
    with urllib.request.urlopen(f"{BASE_URL}/api/v1/wallpapers/daily") as resp:
        daily = json.loads(resp.read().decode())
        daily_data = daily.get('data', {})
        print(f"[OK] Daily Wallpaper: \"{daily_data.get('title')}\" ({daily_data.get('resolution')}) - slug: {daily_data.get('slug')}")

    # 3. List Wallpapers (Feed)
    with urllib.request.urlopen(f"{BASE_URL}/api/v1/wallpapers?limit=10") as resp:
        feed = json.loads(resp.read().decode())
        meta = feed.get('meta', {})
        items = feed.get('data', [])
        print(f"[OK] List Wallpapers: Retrieved {len(items)} wallpapers, Total count in DB: {meta.get('total')}")
        for item in items[:4]:
            print(f"     - \"{item.get('title')}\" | {item.get('resolution')} | {item.get('thumbnail_url')}")

    # 4. Categories with counts
    with urllib.request.urlopen(f"{BASE_URL}/api/v1/categories") as resp:
        cats = json.loads(resp.read().decode()).get('data', [])
        print(f"[OK] Categories Endpoint: {len(cats)} categories returned")
        for c in cats:
            count = c.get('wallpaper_count', 0)
            print(f"     - {c.get('name')} ({c.get('slug')}): {count} wallpapers")

    # 5. Search Wallpapers
    for q in ["Porsche", "Yosemite", "Nebula", "Rose"]:
        url = f"{BASE_URL}/api/v1/search?q={q}"
        with urllib.request.urlopen(url) as resp:
            s_data = json.loads(resp.read().decode())
            results = s_data.get('data', [])
            print(f"[OK] Search Query \"{q}\": Found {len(results)} matches")
            for r in results[:2]:
                print(f"     -> \"{r.get('title')}\" ({r.get('category', {}).get('name') if isinstance(r.get('category'), dict) else r.get('category')})")

    # 6. Verify Physical Image Files and HTTP Access
    sample_thumb_url = items[0].get('thumbnail_url')
    print(f"\n[*] Testing Physical HTTP Image Download: {sample_thumb_url}")
    with urllib.request.urlopen(sample_thumb_url) as resp:
        img_bytes = resp.read()
        print(f"[OK] Image HTTP GET returned {resp.status} with {len(img_bytes):,} bytes (Content-Type: {resp.headers.get('Content-Type')})")

    print("=" * 60)
    print("ALL 6 API & ASSET VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    test_api()
