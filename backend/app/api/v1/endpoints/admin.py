import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db, require_admin, require_super_admin
from app.core.constants import ReportStatus, UserRole
from app.models.user import User
from app.schemas.admin import (
    AdminAnalyticsPoint,
    AdminDashboardMetrics,
    AdminReportResolve,
    AdminUserRoleUpdate,
    AdminUserStatusUpdate,
)
from app.schemas.common import PaginatedResponse, StandardResponse
from app.schemas.interaction import ReportResponse
from app.schemas.user import UserResponse
from app.schemas.wallpaper import WallpaperResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin Operations"], dependencies=[Depends(require_admin)])

@router.get(
    "/dashboard",
    response_model=StandardResponse[AdminDashboardMetrics],
    status_code=status.HTTP_200_OK,
    summary="Get aggregated administrator dashboard KPIs and recent activity"
)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    service = AdminService(db)
    metrics = await service.get_dashboard_metrics()
    return StandardResponse(success=True, data=metrics, message="Admin dashboard metrics retrieved")

@router.get(
    "/wallpapers",
    response_model=PaginatedResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="List all wallpapers with administrative filter criteria"
)
async def list_wallpapers(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    category_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.list_wallpapers(
        page=pagination.page,
        limit=pagination.limit,
        search=search,
        is_published=is_published,
        category_id=category_id
    )

@router.patch(
    "/wallpapers/{wallpaper_id}/publish",
    response_model=StandardResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="Toggle wallpaper publication status"
)
async def toggle_publish(wallpaper_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = AdminService(db)
    updated = await service.toggle_wallpaper_publish(wallpaper_id)
    return StandardResponse(success=True, data=updated, message="Wallpaper publication status updated")

@router.patch(
    "/wallpapers/{wallpaper_id}/feature",
    response_model=StandardResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="Toggle wallpaper featured status"
)
async def toggle_feature(wallpaper_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = AdminService(db)
    updated = await service.toggle_wallpaper_featured(wallpaper_id)
    return StandardResponse(success=True, data=updated, message="Wallpaper featured status updated")

@router.patch(
    "/wallpapers/{wallpaper_id}/daily",
    response_model=StandardResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="Set wallpaper as the daily spotlight"
)
async def set_daily(wallpaper_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = AdminService(db)
    updated = await service.set_wallpaper_daily(wallpaper_id)
    return StandardResponse(success=True, data=updated, message="Daily wallpaper spotlight updated")

@router.delete(
    "/wallpapers/{wallpaper_id}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Permanently delete wallpaper"
)
async def delete_wallpaper(wallpaper_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = AdminService(db)
    await service.delete_wallpaper(wallpaper_id)
    return StandardResponse(success=True, data={"deleted": True}, message="Wallpaper deleted successfully")

@router.get(
    "/users",
    response_model=PaginatedResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List registered users with status and role filtering"
)
async def list_users(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.list_users(page=pagination.page, limit=pagination.limit, search=search, role=role)

@router.patch(
    "/users/{user_id}/status",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Activate or deactivate user account"
)
async def update_user_status(
    user_id: uuid.UUID,
    payload: AdminUserStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    updated = await service.update_user_status(user_id, payload.is_active)
    return StandardResponse(success=True, data=updated, message="User status updated")

@router.patch(
    "/users/{user_id}/role",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Update user role (Super Admin only)",
    dependencies=[Depends(require_super_admin)]
)
async def update_user_role(
    user_id: uuid.UUID,
    payload: AdminUserRoleUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    updated = await service.update_user_role(user_id, payload.role)
    return StandardResponse(success=True, data=updated, message="User role updated")

@router.get(
    "/reports",
    response_model=PaginatedResponse[ReportResponse],
    status_code=status.HTTP_200_OK,
    summary="List reported wallpapers queue"
)
async def list_reports(
    pagination: PaginationParams = Depends(),
    report_status: Optional[ReportStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.list_reports(page=pagination.page, limit=pagination.limit, status=report_status)

@router.patch(
    "/reports/{report_id}/resolve",
    response_model=StandardResponse[ReportResponse],
    status_code=status.HTTP_200_OK,
    summary="Resolve or dismiss content report"
)
async def resolve_report(
    report_id: uuid.UUID,
    payload: AdminReportResolve,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    result = await service.resolve_report(
        report_id=report_id,
        reviewer_id=current_admin.id,
        payload=payload
    )
    return StandardResponse(success=True, data=result, message="Report resolved")

@router.get(
    "/analytics",
    response_model=StandardResponse[List[AdminAnalyticsPoint]],
    status_code=status.HTTP_200_OK,
    summary="Get 7-day engagement time-series for administration charts"
)
async def get_analytics(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    points = await service.get_analytics_timeseries(days=days)
    return StandardResponse(success=True, data=points, message="Analytics timeseries retrieved")
