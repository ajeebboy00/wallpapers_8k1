import uuid
from typing import List, Optional, Tuple
from sqlalchemy import delete, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import ReportReason, ReportStatus
from app.models.download import Download
from app.models.favorite import Favorite
from app.models.report import Report
from app.models.share import WallpaperShare
from app.models.view import WallpaperView
from app.models.wallpaper import Wallpaper

class InteractionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _recalculate_trending_score(self, wp: Wallpaper) -> float:
        """Calculates trending score based on multi-factor weighted engagement."""
        score = (
            (wp.view_count * 0.1) +
            (wp.download_count * 2.0) +
            (wp.favorite_count * 3.0) +
            (wp.share_count * 2.5)
        )
        return round(score, 2)

    async def get_wallpaper_by_id(self, wallpaper_id: uuid.UUID) -> Optional[Wallpaper]:
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

    async def is_favorite(self, user_id: uuid.UUID, wallpaper_id: uuid.UUID) -> bool:
        stmt = select(func.count(Favorite.id)).where(
            Favorite.user_id == user_id,
            Favorite.wallpaper_id == wallpaper_id
        )
        count = (await self.session.execute(stmt)).scalar() or 0
        return count > 0

    async def add_favorite(self, user_id: uuid.UUID, wallpaper_id: uuid.UUID) -> Tuple[bool, int]:
        wp = await self.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            return False, 0

        already_favorite = await self.is_favorite(user_id, wallpaper_id)
        if not already_favorite:
            favorite = Favorite(user_id=user_id, wallpaper_id=wallpaper_id)
            self.session.add(favorite)
            wp.favorite_count += 1
            wp.trending_score = self._recalculate_trending_score(wp)
            await self.session.commit()
            await self.session.refresh(wp)

        return True, wp.favorite_count

    async def remove_favorite(self, user_id: uuid.UUID, wallpaper_id: uuid.UUID) -> Tuple[bool, int]:
        wp = await self.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            return False, 0

        already_favorite = await self.is_favorite(user_id, wallpaper_id)
        if already_favorite:
            stmt = delete(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.wallpaper_id == wallpaper_id
            )
            await self.session.execute(stmt)
            if wp.favorite_count > 0:
                wp.favorite_count -= 1
            wp.trending_score = self._recalculate_trending_score(wp)
            await self.session.commit()
            await self.session.refresh(wp)

        return False, wp.favorite_count

    async def record_download(
        self,
        wallpaper_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None
    ) -> Tuple[Download, int, str]:
        wp = await self.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            return None, 0, ""

        download = Download(
            wallpaper_id=wallpaper_id,
            user_id=user_id
        )
        self.session.add(download)
        wp.download_count += 1
        wp.trending_score = self._recalculate_trending_score(wp)
        await self.session.commit()
        await self.session.refresh(wp)
        await self.session.refresh(download)

        return download, wp.download_count, wp.original_url

    async def record_view(
        self,
        wallpaper_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        session_identifier: Optional[str] = None
    ) -> int:
        wp = await self.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            return 0

        view = WallpaperView(
            wallpaper_id=wallpaper_id,
            user_id=user_id,
            session_identifier=session_identifier
        )
        self.session.add(view)
        wp.view_count += 1
        wp.trending_score = self._recalculate_trending_score(wp)
        await self.session.commit()
        await self.session.refresh(wp)

        return wp.view_count

    async def record_share(
        self,
        wallpaper_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        platform: Optional[str] = None
    ) -> int:
        wp = await self.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            return 0

        share = WallpaperShare(
            wallpaper_id=wallpaper_id,
            user_id=user_id,
            platform=platform
        )
        self.session.add(share)
        wp.share_count += 1
        wp.trending_score = self._recalculate_trending_score(wp)
        await self.session.commit()
        await self.session.refresh(wp)

        return wp.share_count

    async def create_report(
        self,
        user_id: uuid.UUID,
        wallpaper_id: uuid.UUID,
        reason: ReportReason,
        description: Optional[str] = None
    ) -> Report:
        report = Report(
            user_id=user_id,
            wallpaper_id=wallpaper_id,
            reason=reason,
            description=description,
            status=ReportStatus.PENDING
        )
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_user_favorites(
        self,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20
    ) -> Tuple[List[Wallpaper], int]:
        # Count total
        count_stmt = (
            select(func.count(Favorite.id))
            .where(Favorite.user_id == user_id)
        )
        total = (await self.session.execute(count_stmt)).scalar() or 0

        # Query wallpapers joined with favorites ordered by favorite created_at
        stmt = (
            select(Wallpaper)
            .join(Favorite, Favorite.wallpaper_id == Wallpaper.id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(offset)
            .limit(limit)
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
        )
        result = await self.session.execute(stmt)
        wallpapers = list(result.scalars().all())
        return wallpapers, total

    async def get_user_downloads(
        self,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20
    ) -> Tuple[List[Wallpaper], int]:
        # Count distinct wallpapers downloaded
        count_stmt = (
            select(func.count(distinct(Download.wallpaper_id)))
            .where(Download.user_id == user_id)
        )
        total = (await self.session.execute(count_stmt)).scalar() or 0

        # Query distinct wallpapers downloaded recently
        stmt = (
            select(Wallpaper)
            .join(Download, Download.wallpaper_id == Wallpaper.id)
            .where(Download.user_id == user_id)
            .group_by(Wallpaper.id)
            .order_by(func.max(Download.created_at).desc())
            .offset(offset)
            .limit(limit)
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
        )
        result = await self.session.execute(stmt)
        wallpapers = list(result.scalars().all())
        return wallpapers, total
