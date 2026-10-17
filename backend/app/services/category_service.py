import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.logging import logger
from app.core.utils import generate_slug
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.cache_service import cache_service

class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CategoryRepository(session)

    async def list_categories(self, active_only: bool = True) -> List[CategoryResponse]:
        """Returns all categories with calculated wallpaper counts (with caching)."""
        cache_key = f"w8k1:categories:list:{active_only}"
        cached_cats = await cache_service.get(cache_key)
        if cached_cats is not None:
            try:
                return [CategoryResponse.model_validate(c) for c in cached_cats]
            except Exception:
                pass

        rows = await self.repo.get_all_with_counts(active_only=active_only)
        responses: List[CategoryResponse] = []
        for cat, count in rows:
            resp = CategoryResponse(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                description=cat.description,
                image_url=cat.image_url,
                sort_order=cat.sort_order,
                is_active=cat.is_active,
                wallpaper_count=count,
                created_at=cat.created_at,
                updated_at=cat.updated_at
            )
            responses.append(resp)
        await cache_service.set(cache_key, [r.model_dump(mode="json") for r in responses], ttl_seconds=600)
        return responses

    async def get_by_slug(self, slug: str) -> CategoryResponse:
        """Retrieves a single category by slug."""
        cat = await self.repo.get_by_slug(slug)
        if not cat:
            raise NotFoundException(f"Category '{slug}' not found", code="CATEGORY_NOT_FOUND")

        count = await self.repo.get_wallpaper_count(cat.id)
        return CategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            image_url=cat.image_url,
            sort_order=cat.sort_order,
            is_active=cat.is_active,
            wallpaper_count=count,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        )

    async def get_by_id(self, category_id: uuid.UUID) -> Category:
        """Internal helper to get raw Category model."""
        cat = await self.repo.get_by_id(category_id)
        if not cat:
            raise NotFoundException(f"Category with ID '{category_id}' not found", code="CATEGORY_NOT_FOUND")
        return cat

    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        """Creates a new category with slug collision avoidance."""
        base_slug = data.slug or generate_slug(data.name, fallback_prefix="category")
        slug = base_slug
        counter = 1
        while await self.repo.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        cat = Category(
            name=data.name,
            slug=slug,
            description=data.description,
            image_url=data.image_url,
            sort_order=data.sort_order,
            is_active=data.is_active
        )
        created = await self.repo.create(cat)
        logger.info(f"Created category: {created.name} ({created.slug})")
        await cache_service.invalidate_prefix("w8k1:categories:list")
        return CategoryResponse.model_validate(created)

    async def update_category(self, category_id: uuid.UUID, data: CategoryUpdate) -> CategoryResponse:
        """Updates category fields."""
        cat = await self.get_by_id(category_id)

        update_dict = data.model_dump(exclude_unset=True)
        if "slug" in update_dict and update_dict["slug"] != cat.slug:
            existing = await self.repo.get_by_slug(update_dict["slug"])
            if existing and existing.id != cat.id:
                raise ConflictException(f"Slug '{update_dict['slug']}' is already in use", code="SLUG_CONFLICT")

        for key, value in update_dict.items():
            setattr(cat, key, value)

        await self.session.flush()
        count = await self.repo.get_wallpaper_count(cat.id)
        resp = CategoryResponse.model_validate(cat)
        resp.wallpaper_count = count
        await cache_service.invalidate_prefix("w8k1:categories:list")
        return resp

    async def delete_category(self, category_id: uuid.UUID) -> None:
        """Deletes a category if it contains no wallpapers."""
        cat = await self.get_by_id(category_id)
        count = await self.repo.get_wallpaper_count(cat.id)
        if count > 0:
            raise ConflictException(
                f"Cannot delete category '{cat.name}' because it contains {count} published wallpapers. Reassign or delete wallpapers first.",
                code="CATEGORY_NOT_EMPTY"
            )
        await self.repo.delete(cat)
        await cache_service.invalidate_prefix("w8k1:categories:list")
        logger.info(f"Deleted category: {cat.name} ({cat.id})")
