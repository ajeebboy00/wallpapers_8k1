import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.upload import ImageUploadResponse
from app.schemas.wallpaper import WallpaperCreate, WallpaperResponse
from app.services.wallpaper_service import WallpaperService
from app.storage import get_storage_provider
from app.storage.base import StorageProvider
from app.storage.image_processor import ImageProcessor, ProcessedImageResult

class UploadService:
    """Service orchestrating image validation, variant generation, storage persistence, and wallpaper creation."""

    def __init__(self, session: AsyncSession, storage: Optional[StorageProvider] = None):
        self.session = session
        self.storage = storage or get_storage_provider()
        self.wallpaper_service = WallpaperService(session)

    async def process_and_store_image(
        self,
        file_bytes: bytes,
        filename: str = "upload.jpg"
    ) -> Tuple[ImageUploadResponse, ProcessedImageResult]:
        """Runs image through processing pipeline and saves multi-tier variants to storage."""
        # 1. Process variants through Pillow pipeline
        processed = ImageProcessor.process_image(file_bytes, filename=filename)

        # 2. Generate structured storage path
        now = datetime.now(timezone.utc)
        unique_id = uuid.uuid4().hex
        base_path = f"wallpapers/{now.year}/{now.month:02d}/{unique_id}"

        orig_path = f"{base_path}_original{processed.original_extension}"
        opt_path = f"{base_path}_optimized.webp"
        prev_path = f"{base_path}_preview.webp"
        thumb_path = f"{base_path}_thumbnail.webp"

        # 3. Persist all 4 variants
        original_url = await self.storage.save(
            processed.original_bytes,
            orig_path,
            f"image/{processed.file_format}"
        )
        image_url = await self.storage.save(
            processed.optimized_bytes,
            opt_path,
            "image/webp"
        )
        preview_url = await self.storage.save(
            processed.preview_bytes,
            prev_path,
            "image/webp"
        )
        thumbnail_url = await self.storage.save(
            processed.thumbnail_bytes,
            thumb_path,
            "image/webp"
        )

        response = ImageUploadResponse(
            original_url=original_url,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            preview_url=preview_url,
            width=processed.width,
            height=processed.height,
            aspect_ratio=processed.aspect_ratio,
            file_size=processed.file_size,
            file_format=processed.file_format,
            resolution=processed.resolution
        )

        return response, processed

    async def upload_and_create_wallpaper(
        self,
        file_bytes: bytes,
        filename: str,
        title: str,
        category_id: uuid.UUID,
        uploader_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_featured: bool = False,
        is_trending: bool = False,
        is_daily: bool = False,
        is_published: bool = True
    ) -> WallpaperResponse:
        """Processes uploaded image file and creates complete Wallpaper database entry in a single transaction."""
        upload_resp, processed = await self.process_and_store_image(file_bytes, filename=filename)

        create_payload = WallpaperCreate(
            title=title,
            description=description,
            category_id=category_id,
            original_url=upload_resp.original_url,
            image_url=upload_resp.image_url,
            thumbnail_url=upload_resp.thumbnail_url,
            preview_url=upload_resp.preview_url,
            width=processed.width,
            height=processed.height,
            file_size=processed.file_size,
            file_format=processed.file_format,
            resolution=processed.resolution,
            tags=tags or [],
            is_featured=is_featured,
            is_trending=is_trending,
            is_daily=is_daily,
            is_published=is_published
        )

        return await self.wallpaper_service.create_wallpaper(create_payload, uploader_id=uploader_id)
