"""
Database Index Profiling & Optimization Utility for Wallpapers_8k1
Runs PostgreSQL ANALYZE and checks query execution plans with EXPLAIN ANALYZE.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.core.config import settings
from app.core.logging import logger


async def profile_database():
    print("=" * 70)
    print("  WALLPAPERS_8K1 (W8K1) - DATABASE PROFILER & OPTIMIZER")
    print("=" * 70)
    print(f"Target Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")

    async with AsyncSessionLocal() as session:
        # 1. Vacuum & Analyze
        print("\n[1/3] Running ANALYZE across key tables...")
        # Inspect available tables
        res = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """))
        existing_tables = [r[0] for r in res.fetchall()]
        print(f"  Existing tables: {', '.join(existing_tables)}")

        for table in existing_tables:
            try:
                await session.execute(text(f"ANALYZE {table};"))
                await session.commit()
                print(f"  [OK] ANALYZE {table} completed.")
            except Exception as e:
                await session.rollback()
                print(f"  [WARN] Failed to analyze {table}: {e}")

        # 2. Inspect Existing Indexes
        print("\n[2/3] Checking active indexes on wallpapers table...")
        index_query = text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'wallpapers'
            ORDER BY indexname;
        """)
        try:
            indexes = await session.execute(index_query)
            for idx_name, idx_def in indexes.fetchall():
                print(f"  * {idx_name}")
        except Exception as e:
            print(f"  [WARN] Index inspection query: {e}")

        # 3. Profile Critical Query Plans with EXPLAIN ANALYZE
        print("\n[3/3] Profiling critical queries with EXPLAIN ANALYZE...")

        test_queries = [
            (
                "Trigram Title Search",
                "EXPLAIN ANALYZE SELECT id, title FROM wallpapers WHERE title % 'amoled' LIMIT 10;"
            ),
            (
                "Category Wallpapers Filter",
                "EXPLAIN ANALYZE SELECT id, title FROM wallpapers WHERE is_published = true ORDER BY created_at DESC LIMIT 20;"
            ),
            (
                "Trending Wallpapers Sorting",
                "EXPLAIN ANALYZE SELECT id, title, trending_score FROM wallpapers WHERE is_published = true ORDER BY trending_score DESC LIMIT 20;"
            ),
            (
                "Dominant Color Proximity",
                "EXPLAIN ANALYZE SELECT id, title, dominant_color FROM wallpapers WHERE dominant_color = '#000000' LIMIT 10;"
            )
        ]

        for query_name, explain_sql in test_queries:
            print(f"\n--- Query: {query_name} ---")
            try:
                result = await session.execute(text(explain_sql))
                plan_lines = result.scalars().all()
                for line in plan_lines:
                    print(f"  {line}")
            except Exception as e:
                print(f"  [WARN] Execution error: {e}")

    print("\n" + "=" * 70)
    print("Database profiling and optimization completed.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(profile_database())
