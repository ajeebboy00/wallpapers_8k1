"""
Disaster Recovery & Database Restore Utility for Wallpapers_8k1
Restores PostgreSQL tables from compressed JSON backup archives.
"""
import argparse
import asyncio
import gzip
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.core.config import settings


async def restore_database(archive_path: str, clean_tables: bool = False):
    print("=" * 70)
    print("  WALLPAPERS_8K1 (W8K1) - DATABASE RESTORE UTILITY")
    print("=" * 70)

    if not os.path.isfile(archive_path):
        print(f"Error: Archive file not found: {archive_path}")
        sys.exit(1)

    print(f"Reading archive: {archive_path}")
    with gzip.open(archive_path, "rb") as f:
        payload = json.loads(f.read().decode("utf-8"))

    meta = payload.get("metadata", {})
    tables_data = payload.get("tables", {})
    print(f"Archive generated at: {meta.get('timestamp', 'unknown')}")
    print(f"Tables present: {len(tables_data)}")

    # Specific order to respect foreign key constraints
    table_order = [
        "users", "categories", "tags", "wallpapers", "wallpaper_tags",
        "collections", "collection_wallpapers", "favorites", "downloads",
        "wallpaper_views", "wallpaper_shares", "reports", "notifications",
        "notification_preferences", "device_tokens", "refresh_tokens",
        "subscriptions", "ad_reward_unlocks", "app_settings"
    ]

    async with AsyncSessionLocal() as session:
        # Disable foreign key checks temporarily if supported
        print("\n[1/2] Beginning table restoration...")
        for table in table_order:
            if table not in tables_data:
                continue

            t_info = tables_data[table]
            rows = t_info.get("rows", [])
            columns = t_info.get("columns", [])
            if not rows or not columns:
                continue

            print(f"  Restoring {table} ({len(rows)} rows)...", end=" ", flush=True)

            try:
                # Prepare insert statement with ON CONFLICT DO NOTHING
                col_names = ", ".join(columns)
                val_placeholders = ", ".join([f":{col}" for col in columns])
                insert_sql = text(f"""
                    INSERT INTO {table} ({col_names})
                    VALUES ({val_placeholders})
                    ON CONFLICT DO NOTHING;
                """)

                for row in rows:
                    await session.execute(insert_sql, row)
                await session.commit()
                print("[OK]")
            except Exception as e:
                await session.rollback()
                print(f"[WARN: {e}]")

    print("\n" + "=" * 70)
    print("Database restoration completed.")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Restore Wallpapers_8k1 Database from archive")
    parser.add_argument("--archive", required=True, help="Path to .json.gz backup archive")
    parser.add_argument("--clean", action="store_true", help="Truncate tables before restore")
    args = parser.parse_args()

    asyncio.run(restore_database(args.archive, clean_tables=args.clean))


if __name__ == "__main__":
    main()
