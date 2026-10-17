from abc import ABC, abstractmethod
from typing import Optional

class StorageProvider(ABC):
    """Abstract interface defining required object and file storage behaviors."""

    @abstractmethod
    async def save(self, file_content: bytes, destination_path: str, content_type: str = "application/octet-stream") -> str:
        """Persists file content at destination_path and returns its public URL."""
        pass

    @abstractmethod
    async def get(self, file_path: str) -> bytes:
        """Retrieves raw file content bytes from file_path."""
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """Removes the file at file_path from storage. Returns True if deleted or already absent."""
        pass

    @abstractmethod
    def get_url(self, file_path: str) -> str:
        """Computes the fully-qualified public URL for a given relative storage path."""
        pass

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """Checks if a file exists at the given relative storage path."""
        pass
