import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging, logger
from app.middleware.error_handler import (
    ErrorHandlingMiddleware,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.rate_limiter import custom_rate_limit_exceeded_handler, limiter
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

from fastapi.middleware.gzip import GZipMiddleware
from app.services.cache_service import cache_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Sequence
    setup_logging()
    logger.info(f"==> Booting {settings.APP_NAME} in [{settings.APP_ENV}] mode.")
    logger.info(f"==> Database target: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")
    logger.info(f"==> Storage provider: {settings.STORAGE_PROVIDER}")
    
    # Initialize Cache Service (Redis with in-memory fallback)
    await cache_service.init()

    # Ensure local upload storage directory exists
    os.makedirs(settings.STORAGE_LOCAL_DIR, exist_ok=True)
    yield
    # Shutdown Sequence
    logger.info(f"==> Gracefully shutting down {settings.APP_NAME}.")
    await cache_service.close()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Wallpapers_8k1 (W8K1) - Production Grade Full-Stack 8K Wallpaper Discovery API",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan
)

# Attach SlowAPI limiter to app state
app.state.limiter = limiter

# Register Exception Handlers
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Register Middleware Stack (Order of execution: RequestId -> SecurityHeaders -> GZip -> Logging -> CORS -> ErrorHandling)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"]
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIdMiddleware)

# Mount Static File Provider for Image Storage
uploads_dir = os.path.abspath(settings.STORAGE_LOCAL_DIR)
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/storage/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Mount Versioned API Routers
app.include_router(api_v1_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "brand": "W8K1",
        "version": "1.0.0",
        "api_v1": "/api/v1",
        "status": "operational",
        "api_docs": "/docs" if settings.APP_DEBUG else "disabled in production"
    }
