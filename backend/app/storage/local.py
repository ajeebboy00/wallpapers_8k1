import os
import aiofiles
from typing import Optional

from app.core.config import settings
from app.core.logging import logger
from app.storage.base import StorageProvider

class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider with security sanitization and async I/O."""

    def __init__(self, base_directory: Optional[str] = None, base_url: Optional[str] = None):
        self.base_dir = base_directory or settings.STORAGE_LOCAL_DIR
        self.base_url = base_url or settings.STORAGE_BASE_URL
        self.abs_base_dir = os.path.abspath(self.base_dir)
        os.makedirs(self.abs_base_dir, exist_ok=True)

    def _resolve_safe_path(self, relative_path: str) -> str:
        """Resolves relative path against base directory, preventing path traversal attacks."""
        normalized = os.path.normpath(relative_path).lstrip("/\\")
        full_path = os.path.abspath(os.path.join(self.abs_base_dir, normalized))
        if os.path.commonpath([self.abs_base_dir, full_path]) != self.abs_base_dir:
            raise ValueError(f"Security exception: Path traversal detected for path '{relative_path}'")
        return full_path

    async def save(self, file_content: bytes, destination_path: str, content_type: str = "application/octet-stream") -> str:
        """Writes binary content to disk asynchronously and returns access URL."""
        full_path = self._resolve_safe_path(destination_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        async with aiofiles.open(full_path, "wb") as f:
            await f.write(file_content)

        logger.debug(f"Saved file to local storage: {full_path} ({len(file_content)} bytes)")
        return self.get_url(destination_path)

    async def get(self, file_path: str) -> bytes:
        """Reads file bytes from disk asynchronously."""
        full_path = self._resolve_safe_path(file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist in local storage")

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete(self, file_path: str) -> bool:
        """Deletes file from local storage."""
        full_path = self._resolve_safe_path(file_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                logger.debug(f"Removed file from local storage: {full_path}")
                return True
            except OSError as exc:
                logger.error(f"Failed to delete local file '{full_path}': {exc}")
                return False
        return True

    def get_url(self, file_path: str) -> str:
        """Builds public HTTP URL for the stored resource."""
        clean_path = file_path.replace("\\", "/").lstrip("/")
        return f"{self.base_url.rstrip('/')}/{clean_path}"

    async def exists(self, file_path: str) -> bool:
        """Checks whether the file exists on the filesystem."""
        try:
            full_path = self._resolve_safe_path(file_path)
            return os.path.exists(full_path)
        except ValueError:
            return False
