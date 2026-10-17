from app.core.config import settings
from app.storage.base import StorageProvider
from app.storage.local import LocalStorageProvider
from app.storage.s3 import S3CompatibleStorageProvider

def get_storage_provider() -> StorageProvider:
    """Factory creating configured storage provider instance."""
    if settings.STORAGE_PROVIDER == "s3":
        return S3CompatibleStorageProvider()
    return LocalStorageProvider()

__all__ = ["StorageProvider", "LocalStorageProvider", "S3CompatibleStorageProvider", "get_storage_provider"]
