import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.collection import Collection, CollectionWallpaper
from app.models.wallpaper import Wallpaper
from app.repositories.base import BaseRepository

class CollectionRepository(BaseRepository[Collection]):
    def __init__(self, session: AsyncSession):
        super().__init__(Collection, session)

    async def get_by_slug(self, slug: str) -> Optional[Collection]:
        stmt = select(Collection).where(Collection.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_collections(
        self,
        offset: int = 0,
        limit: int = 20,
        is_featured: Optional[bool] = None,
        is_published: Optional[bool] = True
    ) -> Tuple[List[Tuple[Collection, int]], int]:
        """Lists collections with wallpaper counts and total collection count."""
        base_query = (
            select(
                Collection,
                func.count(CollectionWallpaper.wallpaper_id).label("wallpaper_count")
            )
            .outerjoin(CollectionWallpaper, CollectionWallpaper.collection_id == Collection.id)
            .group_by(Collection.id)
        )

        if is_published is not None:
            base_query = base_query.where(Collection.is_published == is_published)
        if is_featured is not None:
            base_query = base_query.where(Collection.is_featured == is_featured)

        # Count total
        count_stmt = select(func.count(Collection.id))
        if is_published is not None:
            count_stmt = count_stmt.where(Collection.is_published == is_published)
        if is_featured is not None:
            count_stmt = count_stmt.where(Collection.is_featured == is_featured)

        total = (await self.session.execute(count_stmt)).scalar() or 0

        paginated = (
            base_query
            .order_by(Collection.is_featured.desc(), Collection.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(paginated)
        items = result.all()
        return [(row[0], row[1]) for row in items], total

    async def get_collection_wallpapers(self, collection_id: uuid.UUID) -> List[Wallpaper]:
        """Retrieves published wallpapers in a collection ordered by sort_order."""
        stmt = (
            select(Wallpaper)
            .join(CollectionWallpaper, CollectionWallpaper.wallpaper_id == Wallpaper.id)
            .where(
                CollectionWallpaper.collection_id == collection_id,
                Wallpaper.is_published.is_(True)
            )
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
            .order_by(CollectionWallpaper.sort_order.asc(), Wallpaper.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_collection_wallpapers(self, collection_id: uuid.UUID, wallpaper_ids: List[uuid.UUID]) -> None:
        """Sets the ordered list of wallpapers for a collection."""
        # Remove existing association entries
        delete_stmt = (
            CollectionWallpaper.__table__.delete()
            .where(CollectionWallpaper.collection_id == collection_id)
        )
        await self.session.execute(delete_stmt)

        # Insert new ordered entries
        for index, wp_id in enumerate(wallpaper_ids):
            entry = CollectionWallpaper(
                collection_id=collection_id,
                wallpaper_id=wp_id,
                sort_order=index
            )
            self.session.add(entry)

        await self.session.flush()
