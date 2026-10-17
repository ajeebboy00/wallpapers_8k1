import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.core.constants import ReportReason, ReportStatus

class FavoriteToggleResponse(BaseModel):
    is_favorite: bool
    favorite_count: int

class FavoriteStatusResponse(BaseModel):
    is_favorite: bool

class DownloadRecordRequest(BaseModel):
    device_info: Optional[str] = Field(None, max_length=255)

class DownloadRecordResponse(BaseModel):
    download_count: int
    download_url: str

class ViewRecordRequest(BaseModel):
    session_identifier: Optional[str] = Field(None, max_length=100)

class ViewRecordResponse(BaseModel):
    view_count: int

class ShareRecordRequest(BaseModel):
    platform: Optional[str] = Field(None, max_length=50, description="Platform e.g. whatsapp, twitter, telegram, native")

class ShareRecordResponse(BaseModel):
    share_count: int

class ReportCreateRequest(BaseModel):
    reason: ReportReason
    description: Optional[str] = Field(None, max_length=1000)

class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wallpaper_id: uuid.UUID
    user_id: uuid.UUID
    reason: ReportReason
    description: Optional[str] = None
    status: ReportStatus
    created_at: datetime
