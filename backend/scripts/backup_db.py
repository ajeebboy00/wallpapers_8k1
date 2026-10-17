"""
Cross-Platform Database Backup Utility for Wallpapers_8k1
Exports all PostgreSQL tables to compressed timestamped JSON/SQL archives.
"""
import asyncio
import gzip
import json
import os
import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.core.config import settings


async def backup_database(backup_dir: str = "backups", retention_days: int = 7):
    print("=" * 70)
    print("  WALLPAPERS_8K1 (W8K1) - DATABASE BACKUP UTILITY")
    print("=" * 70)

    # Resolve backup path
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    full_backup_dir = os.path.join(root_dir, backup_dir)
    os.makedirs(full_backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"w8k1_backup_{timestamp}.json.gz"
    archive_path = os.path.join(full_backup_dir, archive_name)

    print(f"Target Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")
    print(f"Destination:     {archive_path}")

    backup_payload = {
        "metadata": {
            "app": settings.APP_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.APP_ENV,
            "version": "1.0.0"
        },
        "tables": {}
    }

    async with AsyncSessionLocal() as session:
        # Get list of base tables
        res = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """))
        tables = [r[0] for r in res.fetchall()]
        print(f"\n[1/3] Discovered {len(tables)} tables to backup.")

        total_rows = 0
        for table in tables:
            print(f"  Exporting {table}...", end=" ", flush=True)
            t_res = await session.execute(text(f"SELECT * FROM {table};"))
            columns = list(t_res.keys())
            rows = [dict(zip(columns, [str(v) if v is not None else None for v in row])) for row in t_res.fetchall()]
            backup_payload["tables"][table] = {
                "columns": columns,
                "row_count": len(rows),
                "rows": rows
            }
            total_rows += len(rows)
            print(f"({len(rows)} rows)")

    # Write compressed payload
    print("\n[2/3] Writing compressed gzip archive...")
    raw_json = json.dumps(backup_payload, indent=2).encode("utf-8")
    with gzip.open(archive_path, "wb") as f:
        f.write(raw_json)

    size_kb = os.path.getsize(archive_path) / 1024
    print(f"  [OK] Archive created successfully: {archive_path} ({size_kb:.1f} KB, {total_rows} total rows)")

    # Retention Pruning
    print(f"\n[3/3] Pruning backups older than {retention_days} days...")
    cutoff_time = time.time() - (retention_days * 86400)
    for fname in os.listdir(full_backup_dir):
        if fname.startswith("w8k1_backup_") and fname.endswith(".json.gz"):
            fpath = os.path.join(full_backup_dir, fname)
            if os.path.getmtime(fpath) < cutoff_time:
                print(f"  Removing stale backup: {fname}")
                os.remove(fpath)

    print("\n" + "=" * 70)
    print("Database backup finished successfully.")
    print("=" * 70)
    return archive_path


if __name__ == "__main__":
    asyncio.run(backup_database())
