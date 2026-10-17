import math
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ReportReason
from app.core.exceptions import NotFoundException
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.interaction import (
    DownloadRecordResponse,
    FavoriteStatusResponse,
    FavoriteToggleResponse,
    ReportResponse,
    ShareRecordResponse,
    ViewRecordResponse,
)
from app.schemas.wallpaper import WallpaperResponse

class InteractionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = InteractionRepository(session)

    async def add_favorite(self, user_id: uuid.UUID, wallpaper_id: uuid.UUID) -> FavoriteToggleResponse:
        wp = await self.repo.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        is_fav, count = await self.repo.add_favorite(user_id, wallpaper_id)
        return FavoriteToggleResponse(is_favorite=is_fav, favorite_count=count)

    async def remove_favorite(self, user_id: uuid.UUID, wallpaper_id: uuid.UUID) -> FavoriteToggleResponse:
        wp = await self.repo.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        is_fav, count = await self.repo.remove_favorite(user_id, wallpaper_id)
        return FavoriteToggleResponse(is_favorite=is_fav, favorite_count=count)

    async def check_favorite(self, user_id: Optional[uuid.UUID], wallpaper_id: uuid.UUID) -> FavoriteStatusResponse:
        if not user_id:
            return FavoriteStatusResponse(is_favorite=False)
        is_fav = await self.repo.is_favorite(user_id, wallpaper_id)
        return FavoriteStatusResponse(is_favorite=is_fav)

    async def record_download(
        self,
        wallpaper_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None
    ) -> DownloadRecordResponse:
        wp = await self.repo.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        _, count, download_url = await self.repo.record_download(wallpaper_id, user_id=user_id)
        return DownloadRecordResponse(download_count=count, download_url=download_url)

    async def record_view(
        self,
        wallpaper_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        session_identifier: Optional[str] = None
    ) -> ViewRecordResponse:
        wp = await self.repo.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        count = await self.repo.record_view(
            wallpaper_id=wallpaper_id,
            user_id=user_id,
            session_identifier=session_identifier
        )
        return ViewRecordResponse(view_count=count)

    async def record_share(
        self,
        wallpaper_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        platform: Optional[str] = None
    ) -> ShareRecordResponse:
        wp = await self.repo.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        count = await self.repo.record_share(
            wallpaper_id=wallpaper_id,
            user_id=user_id,
            platform=platform
        )
        return ShareRecordResponse(share_count=count)

    async def create_report(
        self,
        user_id: uuid.UUID,
        wallpaper_id: uuid.UUID,
        reason: ReportReason,
        description: Optional[str] = None
    ) -> ReportResponse:
        wp = await self.repo.get_wallpaper_by_id(wallpaper_id)
        if not wp:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        report = await self.repo.create_report(
            user_id=user_id,
            wallpaper_id=wallpaper_id,
            reason=reason,
            description=description
        )
        return ReportResponse.model_validate(report)

    async def get_user_favorites(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        limit: int = 20
    ) -> PaginatedResponse[WallpaperResponse]:
        offset = (page - 1) * limit
        items, total = await self.repo.get_user_favorites(user_id, offset=offset, limit=limit)

        total_pages = math.ceil(total / limit) if total > 0 else 1
        meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        data = [WallpaperResponse.model_validate(w) for w in items]
        return PaginatedResponse(
            success=True,
            data=data,
            meta=meta,
            message="User favorites retrieved"
        )

    async def get_user_downloads(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        limit: int = 20
    ) -> PaginatedResponse[WallpaperResponse]:
        offset = (page - 1) * limit
        items, total = await self.repo.get_user_downloads(user_id, offset=offset, limit=limit)

        total_pages = math.ceil(total / limit) if total > 0 else 1
        meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        data = [WallpaperResponse.model_validate(w) for w in items]
        return PaginatedResponse(
            success=True,
            data=data,
            meta=meta,
            message="User downloads retrieved"
        )
