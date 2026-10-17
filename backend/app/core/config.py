import os
from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Wallpapers_8k1"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security & Tokens
    SECRET_KEY: str = "default_insecure_secret_key_change_in_production_32chars"
    JWT_SECRET: str = "default_insecure_jwt_secret_key_change_in_prod_32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://w8k1_user:w8k1_secure_password@localhost:5432/wallpapers_8k1_db"

    # Storage
    STORAGE_PROVIDER: str = "local"  # "local" or "s3"
    STORAGE_LOCAL_DIR: str = "storage/uploads"
    STORAGE_BASE_URL: str = "http://localhost:8000/storage/uploads"

    # S3 Storage (Optional)
    STORAGE_BUCKET_NAME: str = ""
    STORAGE_ENDPOINT_URL: str = ""
    STORAGE_ACCESS_KEY: str = ""
    STORAGE_SECRET_KEY: str = ""
    STORAGE_REGION: str = "us-east-1"

    # Admin seed
    SUPERADMIN_EMAIL: str = "admin@wallpapers8k1.com"
    SUPERADMIN_PASSWORD: str = "AdminSecurePassword123!"
    SUPERADMIN_NAME: str = "Wallpapers 8K1 Administrator"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    # Redis & Caching
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    ENABLE_CACHE: bool = True

    # Database Connection Pool
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Firebase Cloud Messaging (Push Notifications)
    FCM_SERVICE_ACCOUNT_JSON: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None

settings = Settings()
