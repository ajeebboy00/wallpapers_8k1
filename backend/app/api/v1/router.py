import os
import sys
import platform
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_request_id
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.collections import router as collections_router
from app.api.v1.endpoints.interactions import router as interactions_router
from app.api.v1.endpoints.monetization import router as monetization_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.search import router as search_router
from app.api.v1.endpoints.subscriptions import router as subscriptions_router
from app.api.v1.endpoints.upload import router as upload_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.wallpapers import router as wallpapers_router
from app.core.config import settings
from app.db.init_db import check_db_health
from app.schemas.common import StandardResponse

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(categories_router)
api_v1_router.include_router(wallpapers_router)
api_v1_router.include_router(collections_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(interactions_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(subscriptions_router)
api_v1_router.include_router(monetization_router)
api_v1_router.include_router(upload_router)
api_v1_router.include_router(admin_router)

@api_v1_router.get(
    "/health",
    response_model=StandardResponse[dict],
    tags=["System"],
    summary="Health check endpoint"
)
async def get_health(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Verifies backend runtime health, database connection, cache status, and storage configuration."""
    from app.services.cache_service import cache_service
    db_ok = await check_db_health(db)
    cache_status = "redis" if cache_service.is_redis_active else "in_memory"
    return StandardResponse(
        success=db_ok,
        data={
            "status": "healthy" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
            "cache": cache_status,
            "environment": settings.APP_ENV,
            "storage_provider": settings.STORAGE_PROVIDER,
            "request_id": get_request_id(request),
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        message="System operational" if db_ok else "Database connection unavailable"
    )

@api_v1_router.get(
    "/health/live",
    tags=["System"],
    summary="Liveness probe for orchestrators"
)
async def get_liveness():
    """Rapid liveness probe (returns 200 OK if process is responding)."""
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}

@api_v1_router.get(
    "/health/ready",
    response_model=StandardResponse[dict],
    tags=["System"],
    summary="Readiness probe for traffic routing"
)
async def get_readiness(
    db: AsyncSession = Depends(get_db)
):
    """Readiness probe checking database connectivity and storage directory writeability."""
    from app.services.cache_service import cache_service
    db_ok = await check_db_health(db)
    storage_ok = os.path.exists(settings.STORAGE_LOCAL_DIR) and os.access(settings.STORAGE_LOCAL_DIR, os.W_OK)
    ready = db_ok and storage_ok

    return StandardResponse(
        success=ready,
        data={
            "ready": ready,
            "database": "connected" if db_ok else "disconnected",
            "storage_writable": storage_ok,
            "cache_active": cache_service.is_redis_active or True,
        },
        message="Service ready for traffic" if ready else "Service not ready"
    )

@api_v1_router.get(
    "/version",
    response_model=StandardResponse[dict],
    tags=["System"],
    summary="API version information"
)
async def get_version(request: Request):
    """Returns the API version, short brand, and documentation links."""
    return StandardResponse(
        success=True,
        data={
            "app_name": settings.APP_NAME,
            "short_brand": "W8K1",
            "api_version": "v1",
            "environment": settings.APP_ENV,
            "debug_mode": settings.APP_DEBUG,
            "python_version": platform.python_version(),
            "docs_url": "/docs" if settings.APP_DEBUG else None,
            "redoc_url": "/redoc" if settings.APP_DEBUG else None,
        },
        message="Wallpapers_8k1 API v1 operational"
    )

@api_v1_router.get(
    "/system/info",
    response_model=StandardResponse[dict],
    tags=["System"],
    summary="Public platform info"
)
async def get_system_info():
    """Returns basic brand identity and public platform capabilities."""
    return StandardResponse(
        success=True,
        data={
            "name": "Wallpapers_8k1",
            "brand": "W8K1",
            "resolutions_supported": ["8K UHD", "4K UHD", "2K QHD", "FHD 1080p"],
            "max_upload_size_mb": 50,
            "allowed_formats": ["JPEG", "PNG", "WEBP"]
        },
        message="Platform metadata"
    )
