import os
from typing import Optional

from app.core.config import settings
from app.core.logging import logger
from app.storage.base import StorageProvider

class S3CompatibleStorageProvider(StorageProvider):
    """Storage provider for AWS S3, Cloudflare R2, MinIO, and other S3-compatible APIs."""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: Optional[str] = None,
    ):
        self.bucket = bucket_name or settings.STORAGE_BUCKET_NAME
        self.endpoint_url = endpoint_url or settings.STORAGE_ENDPOINT_URL or None
        self.access_key = access_key or settings.STORAGE_ACCESS_KEY
        self.secret_key = secret_key or settings.STORAGE_SECRET_KEY
        self.region = region or settings.STORAGE_REGION

    def _get_client(self):
        """Lazy loader for boto3 S3 client to keep local development dependency-free."""
        try:
            import boto3
            from botocore.config import Config
        except ImportError:
            raise RuntimeError("boto3 is required for S3CompatibleStorageProvider. Install it via pip.")

        session = boto3.session.Session()
        return session.client(
            "s3",
            region_name=self.region,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4")
        )

    async def save(self, file_content: bytes, destination_path: str, content_type: str = "application/octet-stream") -> str:
        """Uploads content to S3 bucket."""
        client = self._get_client()
        clean_key = destination_path.replace("\\", "/").lstrip("/")

        client.put_object(
            Bucket=self.bucket,
            Key=clean_key,
            Body=file_content,
            ContentType=content_type
        )
        logger.debug(f"Uploaded object to S3: s3://{self.bucket}/{clean_key}")
        return self.get_url(destination_path)

    async def get(self, file_path: str) -> bytes:
        """Downloads object bytes from S3 bucket."""
        client = self._get_client()
        clean_key = file_path.replace("\\", "/").lstrip("/")
        resp = client.get_object(Bucket=self.bucket, Key=clean_key)
        return resp["Body"].read()

    async def delete(self, file_path: str) -> bool:
        """Deletes object from S3 bucket."""
        client = self._get_client()
        clean_key = file_path.replace("\\", "/").lstrip("/")
        try:
            client.delete_object(Bucket=self.bucket, Key=clean_key)
            logger.debug(f"Deleted object from S3: s3://{self.bucket}/{clean_key}")
            return True
        except Exception as exc:
            logger.error(f"Failed to delete S3 object '{clean_key}': {exc}")
            return False

    def get_url(self, file_path: str) -> str:
        """Constructs public URL for object."""
        clean_key = file_path.replace("\\", "/").lstrip("/")
        if self.endpoint_url:
            return f"{self.endpoint_url.rstrip('/')}/{self.bucket}/{clean_key}"
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{clean_key}"

    async def exists(self, file_path: str) -> bool:
        """Checks object existence via HeadObject."""
        client = self._get_client()
        clean_key = file_path.replace("\\", "/").lstrip("/")
        try:
            client.head_object(Bucket=self.bucket, Key=clean_key)
            return True
        except Exception:
            return False
