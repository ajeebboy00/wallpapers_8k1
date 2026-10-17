import uuid
from typing import List, Optional, Tuple
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.tag import Tag, wallpaper_tags
from app.models.wallpaper import Wallpaper
from app.repositories.base import BaseRepository
from app.schemas.wallpaper import WallpaperFilterParams

class WallpaperRepository(BaseRepository[Wallpaper]):
    def __init__(self, session: AsyncSession):
        super().__init__(Wallpaper, session)

    async def get_by_id(self, wallpaper_id: uuid.UUID) -> Optional[Wallpaper]:
        """Fetch wallpaper by ID with category and tags preloaded."""
        stmt = (
            select(Wallpaper)
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
            .where(Wallpaper.id == wallpaper_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Wallpaper]:
        """Fetch wallpaper by slug with category and tags preloaded."""
        stmt = (
            select(Wallpaper)
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
            .where(Wallpaper.slug == slug)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_or_slug(self, identifier: str) -> Optional[Wallpaper]:
        """Convenience resolver for either UUID or slug."""
        try:
            val_uuid = uuid.UUID(identifier)
            return await self.get_by_id(val_uuid)
        except ValueError:
            return await self.get_by_slug(identifier)

    async def list_wallpapers(
        self,
        filters: WallpaperFilterParams,
        offset: int = 0,
        limit: int = 20
    ) -> Tuple[List[Wallpaper], int]:
        """Queries wallpapers with dynamic filtering, sorting, and total count."""
        base_query = select(Wallpaper).distinct()

        # Join category if filtered by slug
        if filters.category_slug:
            base_query = base_query.join(Category, Category.id == Wallpaper.category_id).where(
                Category.slug == filters.category_slug
            )
        elif filters.category_id:
            base_query = base_query.where(Wallpaper.category_id == filters.category_id)

        # Join tags if filtered by tag slug
        if filters.tag_slug:
            base_query = (
                base_query
                .join(wallpaper_tags, wallpaper_tags.c.wallpaper_id == Wallpaper.id)
                .join(Tag, Tag.id == wallpaper_tags.c.tag_id)
                .where(Tag.slug == filters.tag_slug)
            )

        # Direct boolean & string filters
        if filters.resolution:
            base_query = base_query.where(Wallpaper.resolution == filters.resolution)
        if filters.is_featured is not None:
            base_query = base_query.where(Wallpaper.is_featured == filters.is_featured)
        if filters.is_trending is not None:
            base_query = base_query.where(Wallpaper.is_trending == filters.is_trending)
        if filters.is_daily is not None:
            base_query = base_query.where(Wallpaper.is_daily == filters.is_daily)
        if filters.is_premium is not None:
            base_query = base_query.where(Wallpaper.is_premium == filters.is_premium)
        if filters.is_published is not None:
            base_query = base_query.where(Wallpaper.is_published == filters.is_published)

        # Count total matching rows
        subq = base_query.subquery()
        count_stmt = select(func.count(distinct(subq.c.id))).select_from(subq)
        total_count = (await self.session.execute(count_stmt)).scalar() or 0

        # Apply sorting
        order_col = Wallpaper.created_at
        if filters.sort == "views":
            order_col = Wallpaper.view_count
        elif filters.sort == "downloads":
            order_col = Wallpaper.download_count
        elif filters.sort == "favorites":
            order_col = Wallpaper.favorite_count
        elif filters.sort == "trending":
            order_col = Wallpaper.trending_score
        elif filters.sort == "oldest":
            order_col = Wallpaper.created_at

        if filters.order == "asc":
            base_query = base_query.order_by(order_col.asc(), Wallpaper.id.asc())
        else:
            base_query = base_query.order_by(order_col.desc(), Wallpaper.id.desc())

        # Pagination & relation loading
        paginated_query = (
            base_query
            .offset(offset)
            .limit(limit)
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
        )

        result = await self.session.execute(paginated_query)
        wallpapers = list(result.scalars().all())

        return wallpapers, total_count

    async def get_daily_wallpaper(self) -> Optional[Wallpaper]:
        """Retrieves the current daily wallpaper, or falls back to latest featured/published."""
        stmt = (
            select(Wallpaper)
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
            .where(Wallpaper.is_published.is_(True), Wallpaper.is_daily.is_(True))
            .order_by(Wallpaper.updated_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        daily = result.scalar_one_or_none()

        if daily:
            return daily

        # Fallback to latest featured
        fallback_stmt = (
            select(Wallpaper)
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
            .where(Wallpaper.is_published.is_(True), Wallpaper.is_featured.is_(True))
            .order_by(Wallpaper.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(fallback_stmt)
        return result.scalar_one_or_none()

    async def get_related_wallpapers(
        self,
        wallpaper_id: uuid.UUID,
        category_id: uuid.UUID,
        tag_ids: List[uuid.UUID],
        limit: int = 10
    ) -> List[Wallpaper]:
        """Finds related wallpapers by matching category and/or tags."""
        stmt = (
            select(Wallpaper)
            .distinct()
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
            .where(
                Wallpaper.id != wallpaper_id,
                Wallpaper.is_published.is_(True)
            )
        )

        if tag_ids:
            stmt = stmt.outerjoin(wallpaper_tags, wallpaper_tags.c.wallpaper_id == Wallpaper.id).where(
                (Wallpaper.category_id == category_id) | (wallpaper_tags.c.tag_id.in_(tag_ids))
            )
        else:
            stmt = stmt.where(Wallpaper.category_id == category_id)

        stmt = stmt.order_by(Wallpaper.view_count.desc(), Wallpaper.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def increment_counter(self, wallpaper_id: uuid.UUID, field_name: str) -> None:
        """Atomically increments interaction counter (view, download, share)."""
        if field_name not in ("view_count", "download_count", "favorite_count", "share_count"):
            return

        column = getattr(Wallpaper, field_name)
        stmt = (
            Wallpaper.__table__.update()
            .where(Wallpaper.id == wallpaper_id)
            .values({field_name: column + 1})
        )
        await self.session.execute(stmt)
