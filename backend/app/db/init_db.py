import asyncio
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger

def ensure_database_exists():
    """Ensure the target PostgreSQL database exists before migrations."""
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite"):
        return

    # Parse connection components
    # URL format: postgresql+asyncpg://user:pass@host:port/dbname
    clean_url = db_url.replace("postgresql+asyncpg://", "").replace("postgresql+psycopg2://", "").replace("postgresql://", "")
    auth_part, host_part = clean_url.split("@") if "@" in clean_url else ("", clean_url)
    user_pass = auth_part.split(":") if auth_part else ["postgres", ""]
    user = user_pass[0] or "postgres"
    password = user_pass[1] if len(user_pass) > 1 else ""
    
    host_port_db = host_part.split("/")
    host_port = host_port_db[0].split(":")
    host = host_port[0] or "localhost"
    port = int(host_port[1]) if len(host_port) > 1 else 5432
    target_db = host_port_db[1] if len(host_port_db) > 1 else "wallpapers_8k1_db"

    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (target_db,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(f'CREATE DATABASE "{target_db}";')
                logger.info(f"Created PostgreSQL database: {target_db}")
            else:
                logger.info(f"PostgreSQL database '{target_db}' already exists.")
        conn.close()
    except Exception as exc:
        logger.warning(f"Could not verify/create database via psycopg2: {exc}")

async def check_db_health(session: AsyncSession) -> bool:
    """Verifies that the database engine can execute queries successfully."""
    try:
        result = await session.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        return False

if __name__ == "__main__":
    ensure_database_exists()
