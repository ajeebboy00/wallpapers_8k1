import uuid
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.constants import ReportStatus, UserRole
from app.schemas.interaction import ReportResponse
from app.schemas.user import UserResponse
from app.schemas.wallpaper import WallpaperResponse

class AdminDashboardMetrics(BaseModel):
    total_wallpapers: int
    total_categories: int
    total_collections: int
    total_users: int
    total_views: int
    total_downloads: int
    total_favorites: int
    total_reports: int
    storage_used_bytes: int
    recent_wallpapers: List[WallpaperResponse] = Field(default_factory=list)
    pending_reports: List[ReportResponse] = Field(default_factory=list)

class AdminUserStatusUpdate(BaseModel):
    is_active: bool

class AdminUserRoleUpdate(BaseModel):
    role: UserRole

class AdminReportResolve(BaseModel):
    status: ReportStatus
    unpublish_wallpaper: bool = False

class AdminAnalyticsPoint(BaseModel):
    date: str
    views: int
    downloads: int
    favorites: int
