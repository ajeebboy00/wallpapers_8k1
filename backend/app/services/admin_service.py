import math
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import ReportStatus, UserRole
from app.core.exceptions import NotFoundException
from app.models.category import Category
from app.models.collection import Collection
from app.models.download import Download
from app.models.favorite import Favorite
from app.models.report import Report
from app.models.user import User
from app.models.view import WallpaperView
from app.models.wallpaper import Wallpaper
from app.schemas.admin import (
    AdminAnalyticsPoint,
    AdminDashboardMetrics,
    AdminReportResolve,
)
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.interaction import ReportResponse
from app.schemas.user import UserResponse
from app.schemas.wallpaper import WallpaperResponse

class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dashboard_metrics(self) -> AdminDashboardMetrics:
        # Aggregated KPI counts
        total_wps = (await self.session.execute(select(func.count(Wallpaper.id)))).scalar() or 0
        total_cats = (await self.session.execute(select(func.count(Category.id)))).scalar() or 0
        total_colls = (await self.session.execute(select(func.count(Collection.id)))).scalar() or 0
        total_users = (await self.session.execute(select(func.count(User.id)))).scalar() or 0

        # Totals for engagement
        total_views = (await self.session.execute(select(func.coalesce(func.sum(Wallpaper.view_count), 0)))).scalar() or 0
        total_downloads = (await self.session.execute(select(func.coalesce(func.sum(Wallpaper.download_count), 0)))).scalar() or 0
        total_favs = (await self.session.execute(select(func.coalesce(func.sum(Wallpaper.favorite_count), 0)))).scalar() or 0
        total_reports = (await self.session.execute(select(func.count(Report.id)).where(Report.status == ReportStatus.PENDING))).scalar() or 0
        storage_bytes = (await self.session.execute(select(func.coalesce(func.sum(Wallpaper.file_size), 0)))).scalar() or 0

        # Recent 5 wallpapers
        wp_stmt = (
            select(Wallpaper)
            .options(selectinload(Wallpaper.category), selectinload(Wallpaper.tags))
            .order_by(Wallpaper.created_at.desc())
            .limit(5)
        )
        recent_wps = list((await self.session.execute(wp_stmt)).scalars().all())

        # Pending 5 reports
        rep_stmt = (
            select(Report)
            .where(Report.status == ReportStatus.PENDING)
            .order_by(Report.created_at.desc())
            .limit(5)
        )
        pending_reps = list((await self.session.execute(rep_stmt)).scalars().all())

        return AdminDashboardMetrics(
            total_wallpapers=total_wps,
            total_categories=total_cats,
            total_collections=total_colls,
            total_users=total_users,
            total_views=total_views,
            total_downloads=total_downloads,
            total_favorites=total_favs,
            total_reports=total_reports,
            storage_used_bytes=storage_bytes,
            recent_wallpapers=[WallpaperResponse.model_validate(w) for w in recent_wps],
            pending_reports=[ReportResponse.model_validate(r) for r in pending_reps],
        )

    async def list_wallpapers(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        is_published: Optional[bool] = None,
        category_id: Optional[uuid.UUID] = None
    ) -> PaginatedResponse[WallpaperResponse]:
        query = select(Wallpaper)
        if search and search.strip():
            kw = f"%{search.strip()}%"
            query = query.where(or_(Wallpaper.title.ilike(kw), Wallpaper.description.ilike(kw)))
        if is_published is not None:
            query = query.where(Wallpaper.is_published == is_published)
        if category_id:
            query = query.where(Wallpaper.category_id == category_id)

        # Count
        count_subq = query.subquery()
        total = (await self.session.execute(select(func.count()).select_from(count_subq))).scalar() or 0

        # Paginate
        offset = (page - 1) * limit
        paginated_stmt = (
            query
            .order_by(Wallpaper.created_at.desc())
            .offset(offset)
            .limit(limit)
            .options(selectinload(Wallpaper.category), selectinload(Wallpaper.tags))
        )
        items = list((await self.session.execute(paginated_stmt)).scalars().all())

        total_pages = math.ceil(total / limit) if total > 0 else 1
        meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        return PaginatedResponse(
            success=True,
            data=[WallpaperResponse.model_validate(w) for w in items],
            meta=meta,
            message="Wallpapers retrieved for admin"
        )

    async def toggle_wallpaper_publish(self, wallpaper_id: uuid.UUID) -> WallpaperResponse:
        stmt = (
            select(Wallpaper)
            .options(selectinload(Wallpaper.category), selectinload(Wallpaper.tags))
            .where(Wallpaper.id == wallpaper_id)
        )
        wp = (await self.session.execute(stmt)).scalar_one_or_none()
        if not wp:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        wp.is_published = not wp.is_published
        await self.session.commit()
        await self.session.refresh(wp)
        return WallpaperResponse.model_validate(wp)

    async def toggle_wallpaper_featured(self, wallpaper_id: uuid.UUID) -> WallpaperResponse:
        stmt = (
            select(Wallpaper)
            .options(selectinload(Wallpaper.category), selectinload(Wallpaper.tags))
            .where(Wallpaper.id == wallpaper_id)
        )
        wp = (await self.session.execute(stmt)).scalar_one_or_none()
        if not wp:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        wp.is_featured = not wp.is_featured
        await self.session.commit()
        await self.session.refresh(wp)
        return WallpaperResponse.model_validate(wp)

    async def set_wallpaper_daily(self, wallpaper_id: uuid.UUID) -> WallpaperResponse:
        stmt = (
            select(Wallpaper)
            .options(selectinload(Wallpaper.category), selectinload(Wallpaper.tags))
            .where(Wallpaper.id == wallpaper_id)
        )
        wp = (await self.session.execute(stmt)).scalar_one_or_none()
        if not wp:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        # Unset other daily
        unmark_stmt = select(Wallpaper).where(Wallpaper.is_daily.is_(True))
        dailies = list((await self.session.execute(unmark_stmt)).scalars().all())
        for d in dailies:
            d.is_daily = False

        wp.is_daily = True
        wp.is_published = True
        await self.session.commit()
        await self.session.refresh(wp)
        return WallpaperResponse.model_validate(wp)

    async def delete_wallpaper(self, wallpaper_id: uuid.UUID) -> bool:
        stmt = select(Wallpaper).where(Wallpaper.id == wallpaper_id)
        wp = (await self.session.execute(stmt)).scalar_one_or_none()
        if not wp:
            raise NotFoundException(f"Wallpaper '{wallpaper_id}' not found", code="WALLPAPER_NOT_FOUND")

        await self.session.delete(wp)
        await self.session.commit()
        return True

    async def list_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        role: Optional[UserRole] = None
    ) -> PaginatedResponse[UserResponse]:
        query = select(User)
        if search and search.strip():
            kw = f"%{search.strip()}%"
            query = query.where(or_(User.name.ilike(kw), User.email.ilike(kw)))
        if role:
            query = query.where(User.role == role)

        count_subq = query.subquery()
        total = (await self.session.execute(select(func.count()).select_from(count_subq))).scalar() or 0

        offset = (page - 1) * limit
        items = list((await self.session.execute(query.order_by(User.created_at.desc()).offset(offset).limit(limit))).scalars().all())

        total_pages = math.ceil(total / limit) if total > 0 else 1
        meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        return PaginatedResponse(
            success=True,
            data=[UserResponse.model_validate(u) for u in items],
            meta=meta,
            message="Users retrieved"
        )

    async def update_user_status(self, user_id: uuid.UUID, is_active: bool) -> UserResponse:
        user = (await self.session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise NotFoundException(f"User '{user_id}' not found", code="USER_NOT_FOUND")

        user.is_active = is_active
        await self.session.commit()
        await self.session.refresh(user)
        return UserResponse.model_validate(user)

    async def update_user_role(self, user_id: uuid.UUID, role: UserRole) -> UserResponse:
        user = (await self.session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise NotFoundException(f"User '{user_id}' not found", code="USER_NOT_FOUND")

        user.role = role
        await self.session.commit()
        await self.session.refresh(user)
        return UserResponse.model_validate(user)

    async def list_reports(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[ReportStatus] = None
    ) -> PaginatedResponse[ReportResponse]:
        query = select(Report)
        if status:
            query = query.where(Report.status == status)

        count_subq = query.subquery()
        total = (await self.session.execute(select(func.count()).select_from(count_subq))).scalar() or 0

        offset = (page - 1) * limit
        items = list((await self.session.execute(query.order_by(Report.created_at.desc()).offset(offset).limit(limit))).scalars().all())

        total_pages = math.ceil(total / limit) if total > 0 else 1
        meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        return PaginatedResponse(
            success=True,
            data=[ReportResponse.model_validate(r) for r in items],
            meta=meta,
            message="Reports retrieved"
        )

    async def resolve_report(
        self,
        report_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        payload: AdminReportResolve
    ) -> ReportResponse:
        report = (await self.session.execute(select(Report).where(Report.id == report_id))).scalar_one_or_none()
        if not report:
            raise NotFoundException(f"Report '{report_id}' not found", code="REPORT_NOT_FOUND")

        report.status = payload.status
        report.reviewed_by = reviewer_id
        report.reviewed_at = datetime.now(timezone.utc)

        if payload.unpublish_wallpaper:
            wp = (await self.session.execute(select(Wallpaper).where(Wallpaper.id == report.wallpaper_id))).scalar_one_or_none()
            if wp:
                wp.is_published = False

        await self.session.commit()
        await self.session.refresh(report)
        return ReportResponse.model_validate(report)

    async def get_analytics_timeseries(self, days: int = 7) -> List[AdminAnalyticsPoint]:
        """Generates real daily timeseries trends for the dashboard chart."""
        points = []
        now = datetime.now(timezone.utc)

        for i in range(days - 1, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            date_str = day_start.strftime("%b %d")

            v_stmt = select(func.count(WallpaperView.id)).where(WallpaperView.created_at >= day_start, WallpaperView.created_at < day_end)
            views = (await self.session.execute(v_stmt)).scalar() or 0

            d_stmt = select(func.count(Download.id)).where(Download.created_at >= day_start, Download.created_at < day_end)
            downloads = (await self.session.execute(d_stmt)).scalar() or 0

            f_stmt = select(func.count(Favorite.id)).where(Favorite.created_at >= day_start, Favorite.created_at < day_end)
            favorites = (await self.session.execute(f_stmt)).scalar() or 0

            points.append(AdminAnalyticsPoint(
                date=date_str,
                views=views,
                downloads=downloads,
                favorites=favorites
            ))

        return points
