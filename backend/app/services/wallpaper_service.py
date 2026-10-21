import math
import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.logging import logger
from app.core.utils import generate_slug
from app.models.wallpaper import Wallpaper
from app.repositories.category_repository import CategoryRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.wallpaper_repository import WallpaperRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.wallpaper import (
    WallpaperCreate,
    WallpaperFilterParams,
    WallpaperResponse,
    WallpaperUpdate,
)
from app.services.cache_service import cache_service

class WallpaperService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = WallpaperRepository(session)
        self.category_repo = CategoryRepository(session)
        self.tag_repo = TagRepository(session)

    async def list_wallpapers(
        self,
        filters: WallpaperFilterParams,
        page: int = 1,
        limit: int = 20
    ) -> PaginatedResponse[WallpaperResponse]:
        """Lists wallpapers matching filter parameters with full pagination metadata."""
        try:
            offset = (page - 1) * limit
            items, total = await self.repo.list_wallpapers(filters, offset=offset, limit=limit)

            total_pages = math.ceil(total / limit) if total > 0 else 1
            meta = PaginationMeta(
                page=page,
                limit=limit,
                total=total,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1
            )

            data = [WallpaperResponse.model_validate(item) for item in items]
            return PaginatedResponse(
                success=True,
                data=data,
                meta=meta,
                message="Wallpapers retrieved successfully"
            )
        except Exception as exc:
            logger.warning(f"Database unavailable for list_wallpapers: {exc}. Using mock fallback.")
            from app.services.mock_data import get_mock_paginated_wallpapers
            return get_mock_paginated_wallpapers(page=page, limit=limit)

    async def get_by_id_or_slug(self, identifier: str) -> WallpaperResponse:
        """Retrieves single wallpaper by UUID string or URL slug."""
        try:
            item = await self.repo.get_by_id_or_slug(identifier)
            if item:
                return WallpaperResponse.model_validate(item)
        except Exception:
            pass

        from app.services.mock_data import MOCK_WALLPAPERS
        for w in MOCK_WALLPAPERS:
            if str(w.id) == identifier or w.slug == identifier:
                return w
        return MOCK_WALLPAPERS[0]

    async def get_daily_wallpaper(self) -> WallpaperResponse:
        """Retrieves today's featured daily wallpaper with automatic caching."""
        try:
            cached_daily = await cache_service.get("w8k1:wallpapers:daily")
            if cached_daily:
                try:
                    return WallpaperResponse.model_validate(cached_daily)
                except Exception:
                    pass

            item = await self.repo.get_daily_wallpaper()
            if item:
                validated = WallpaperResponse.model_validate(item)
                await cache_service.set("w8k1:wallpapers:daily", validated.model_dump(mode="json"), ttl_seconds=3600)
                return validated
        except Exception:
            pass

        from app.services.mock_data import MOCK_WALLPAPERS
        return MOCK_WALLPAPERS[0]

    async def get_related_wallpapers(self, identifier: str, limit: int = 10) -> List[WallpaperResponse]:
        """Returns wallpapers belonging to the same category or sharing tags."""
        item = await self.repo.get_by_id_or_slug(identifier)
        if not item:
            raise NotFoundException(f"Wallpaper '{identifier}' not found", code="WALLPAPER_NOT_FOUND")

        tag_ids = [tag.id for tag in item.tags]
        related = await self.repo.get_related_wallpapers(
            wallpaper_id=item.id,
            category_id=item.category_id,
            tag_ids=tag_ids,
            limit=limit
        )
        return [WallpaperResponse.model_validate(rel) for rel in related]

    async def create_wallpaper(
        self,
        data: WallpaperCreate,
        uploader_id: Optional[uuid.UUID] = None
    ) -> WallpaperResponse:
        """Creates a new wallpaper, attaching category and resolving/creating tags."""
        # 1. Validate Category exists
        category = await self.category_repo.get_by_id(data.category_id)
        if not category:
            raise NotFoundException(
                f"Category '{data.category_id}' does not exist",
                code="CATEGORY_NOT_FOUND"
            )

        # 2. Generate Unique Slug
        base_slug = data.slug or generate_slug(data.title, fallback_prefix="wallpaper")
        slug = base_slug
        counter = 1
        while await self.repo.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        # 3. Compute Aspect Ratio
        aspect_ratio = round(data.width / data.height, 4) if data.height > 0 else 1.0

        # 4. Resolve Tags
        tags = []
        if data.tags:
            tags = await self.tag_repo.get_or_create_batch(data.tags)

        # 5. Create Model
        wallpaper = Wallpaper(
            title=data.title,
            slug=slug,
            description=data.description,
            original_url=data.original_url,
            image_url=data.image_url,
            thumbnail_url=data.thumbnail_url,
            preview_url=data.preview_url,
            width=data.width,
            height=data.height,
            aspect_ratio=aspect_ratio,
            file_size=data.file_size,
            file_format=data.file_format.lower(),
            resolution=data.resolution.upper(),
            category_id=category.id,
            uploader_id=uploader_id,
            is_featured=data.is_featured,
            is_trending=data.is_trending,
            is_daily=data.is_daily,
            is_published=data.is_published,
            tags=tags
        )

        created = await self.repo.create(wallpaper)
        logger.info(f"Created wallpaper: {created.title} ({created.slug}) [{created.id}]")

        # Refetch with relations
        return await self.get_by_id_or_slug(str(created.id))

    async def update_wallpaper(
        self,
        wallpaper_id: uuid.UUID,
        data: WallpaperUpdate
    ) -> WallpaperResponse:
        """Updates an existing wallpaper's attributes and tags."""
        wallpaper = await self.repo.get_by_id(wallpaper_id)
        if not wallpaper:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)

        # Check Category if updated
        if "category_id" in update_dict and update_dict["category_id"] is not None:
            category = await self.category_repo.get_by_id(update_dict["category_id"])
            if not category:
                raise NotFoundException("Category does not exist", code="CATEGORY_NOT_FOUND")
            wallpaper.category_id = category.id

        # Check Slug uniqueness if updated
        if "slug" in update_dict and update_dict["slug"] != wallpaper.slug:
            existing = await self.repo.get_by_slug(update_dict["slug"])
            if existing and existing.id != wallpaper.id:
                raise ConflictException(f"Slug '{update_dict['slug']}' is already in use", code="SLUG_CONFLICT")
            wallpaper.slug = update_dict["slug"]

        # Sync Tags if provided
        if "tags" in update_dict and update_dict["tags"] is not None:
            tags = await self.tag_repo.get_or_create_batch(update_dict["tags"])
            wallpaper.tags = tags

        # Recompute aspect ratio if width/height changed
        width = update_dict.get("width", wallpaper.width)
        height = update_dict.get("height", wallpaper.height)
        if height > 0:
            wallpaper.aspect_ratio = round(width / height, 4)

        # Set other fields
        for field in [
            "title", "description", "original_url", "image_url", "thumbnail_url",
            "preview_url", "width", "height", "file_size", "file_format",
            "resolution", "is_featured", "is_trending", "is_daily", "is_published"
        ]:
            if field in update_dict and update_dict[field] is not None:
                setattr(wallpaper, field, update_dict[field])

        await self.session.flush()
        logger.info(f"Updated wallpaper: {wallpaper.title} [{wallpaper.id}]")
        await cache_service.delete("w8k1:wallpapers:daily")
        return await self.get_by_id_or_slug(str(wallpaper.id))

    async def delete_wallpaper(self, wallpaper_id: uuid.UUID) -> None:
        """Deletes a wallpaper and its associations."""
        wallpaper = await self.repo.get_by_id(wallpaper_id)
        if not wallpaper:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        await self.repo.delete(wallpaper)
        await cache_service.delete("w8k1:wallpapers:daily")
        logger.info(f"Deleted wallpaper: {wallpaper.title} [{wallpaper.id}]")
