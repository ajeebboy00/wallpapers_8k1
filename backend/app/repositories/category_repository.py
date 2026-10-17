import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.wallpaper import Wallpaper
from app.repositories.base import BaseRepository

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(Category, session)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """Fetch category by unique URL slug."""
        stmt = select(Category).where(Category.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_counts(self, active_only: bool = True) -> List[Tuple[Category, int]]:
        """Fetch categories ordered by sort_order alongside active published wallpaper count."""
        # Count wallpapers subquery
        stmt = (
            select(
                Category,
                func.count(Wallpaper.id).filter(Wallpaper.is_published.is_(True)).label("wallpaper_count")
            )
            .outerjoin(Wallpaper, Wallpaper.category_id == Category.id)
            .group_by(Category.id)
            .order_by(Category.sort_order.asc(), Category.name.asc())
        )
        if active_only:
            stmt = stmt.where(Category.is_active.is_(True))

        result = await self.session.execute(stmt)
        return result.all()

    async def get_wallpaper_count(self, category_id: uuid.UUID) -> int:
        """Count total published wallpapers in a specific category."""
        stmt = (
            select(func.count(Wallpaper.id))
            .where(Wallpaper.category_id == category_id, Wallpaper.is_published.is_(True))
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
