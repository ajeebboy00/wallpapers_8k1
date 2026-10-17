import math
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.logging import logger
from app.core.utils import generate_slug
from app.models.collection import Collection
from app.repositories.collection_repository import CollectionRepository
from app.repositories.wallpaper_repository import WallpaperRepository
from app.schemas.collection import (
    CollectionCreate,
    CollectionDetailResponse,
    CollectionResponse,
    CollectionUpdate,
)
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.wallpaper import WallpaperResponse

class CollectionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CollectionRepository(session)
        self.wallpaper_repo = WallpaperRepository(session)

    async def list_collections(
        self,
        page: int = 1,
        limit: int = 20,
        is_featured: Optional[bool] = None,
        is_published: Optional[bool] = True
    ) -> PaginatedResponse[CollectionResponse]:
        """Lists collections with pagination and wallpaper counts."""
        offset = (page - 1) * limit
        items, total = await self.repo.list_collections(
            offset=offset,
            limit=limit,
            is_featured=is_featured,
            is_published=is_published
        )

        total_pages = math.ceil(total / limit) if total > 0 else 1
        meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )

        data = []
        for coll, count in items:
            resp = CollectionResponse(
                id=coll.id,
                name=coll.name,
                slug=coll.slug,
                description=coll.description,
                cover_image_url=coll.cover_image_url,
                is_featured=coll.is_featured,
                is_published=coll.is_published,
                wallpaper_count=count,
                created_at=coll.created_at,
                updated_at=coll.updated_at
            )
            data.append(resp)

        return PaginatedResponse(
            success=True,
            data=data,
            meta=meta,
            message="Collections retrieved successfully"
        )

    async def get_collection(self, identifier: str) -> CollectionDetailResponse:
        """Retrieves collection with full list of constituent wallpapers."""
        coll = None
        try:
            val_uuid = uuid.UUID(identifier)
            coll = await self.repo.get_by_id(val_uuid)
        except ValueError:
            coll = await self.repo.get_by_slug(identifier)

        if not coll:
            raise NotFoundException(f"Collection '{identifier}' not found", code="COLLECTION_NOT_FOUND")

        wallpapers = await self.repo.get_collection_wallpapers(coll.id)
        wp_responses = [WallpaperResponse.model_validate(w) for w in wallpapers]

        return CollectionDetailResponse(
            id=coll.id,
            name=coll.name,
            slug=coll.slug,
            description=coll.description,
            cover_image_url=coll.cover_image_url,
            is_featured=coll.is_featured,
            is_published=coll.is_published,
            wallpaper_count=len(wp_responses),
            created_at=coll.created_at,
            updated_at=coll.updated_at,
            wallpapers=wp_responses
        )

    async def create_collection(self, data: CollectionCreate) -> CollectionResponse:
        """Creates a new collection, generating unique slug and assigning wallpapers."""
        base_slug = data.slug or generate_slug(data.name, fallback_prefix="collection")
        slug = base_slug
        counter = 1
        while await self.repo.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        collection = Collection(
            name=data.name,
            slug=slug,
            description=data.description,
            cover_image_url=data.cover_image_url,
            is_featured=data.is_featured,
            is_published=data.is_published
        )
        created = await self.repo.create(collection)

        if data.wallpaper_ids:
            await self.repo.set_collection_wallpapers(created.id, data.wallpaper_ids)

        logger.info(f"Created collection: {created.name} ({created.slug})")
        return CollectionResponse(
            id=created.id,
            name=created.name,
            slug=created.slug,
            description=created.description,
            cover_image_url=created.cover_image_url,
            is_featured=created.is_featured,
            is_published=created.is_published,
            wallpaper_count=len(data.wallpaper_ids) if data.wallpaper_ids else 0,
            created_at=created.created_at,
            updated_at=created.updated_at
        )

    async def update_collection(self, collection_id: uuid.UUID, data: CollectionUpdate) -> CollectionResponse:
        """Updates collection metadata and ordered wallpaper membership."""
        coll = await self.repo.get_by_id(collection_id)
        if not coll:
            raise NotFoundException(f"Collection '{collection_id}' not found", code="COLLECTION_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)
        if "slug" in update_dict and update_dict["slug"] != coll.slug:
            existing = await self.repo.get_by_slug(update_dict["slug"])
            if existing and existing.id != coll.id:
                raise ConflictException(f"Slug '{update_dict['slug']}' is already in use", code="SLUG_CONFLICT")
            coll.slug = update_dict["slug"]

        for field in ["name", "description", "cover_image_url", "is_featured", "is_published"]:
            if field in update_dict and update_dict[field] is not None:
                setattr(coll, field, update_dict[field])

        if "wallpaper_ids" in update_dict and update_dict["wallpaper_ids"] is not None:
            await self.repo.set_collection_wallpapers(coll.id, update_dict["wallpaper_ids"])

        await self.session.flush()
        wallpapers = await self.repo.get_collection_wallpapers(coll.id)

        return CollectionResponse(
            id=coll.id,
            name=coll.name,
            slug=coll.slug,
            description=coll.description,
            cover_image_url=coll.cover_image_url,
            is_featured=coll.is_featured,
            is_published=coll.is_published,
            wallpaper_count=len(wallpapers),
            created_at=coll.created_at,
            updated_at=coll.updated_at
        )

    async def delete_collection(self, collection_id: uuid.UUID) -> None:
        """Deletes a collection."""
        coll = await self.repo.get_by_id(collection_id)
        if not coll:
            raise NotFoundException(f"Collection '{collection_id}' not found", code="COLLECTION_NOT_FOUND")
        await self.repo.delete(coll)
        logger.info(f"Deleted collection: {coll.name} [{coll.id}]")
