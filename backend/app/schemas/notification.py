import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import NotificationType

class DeviceTokenCreate(BaseModel):
    token: str = Field(..., min_length=10, max_length=512, description="FCM device push registration token")
    device_id: Optional[str] = Field(None, max_length=128, description="Unique client hardware or install identifier")
    platform: str = Field("android", max_length=30, description="Client platform: android, ios, web")
    app_version: Optional[str] = Field(None, max_length=50, description="Client application build version")
    topics: Optional[List[str]] = Field(default_factory=list, description="Subscribed notification topics")

class DeviceTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    token: str
    device_id: Optional[str] = None
    platform: str
    app_version: Optional[str] = None
    is_active: bool
    topics: List[str] = Field(default_factory=list)
    created_at: datetime
    last_seen_at: datetime

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    title: str
    message: str
    type: NotificationType
    data: Optional[Dict[str, Any]] = None
    is_read: bool
    created_at: datetime

class NotificationUnreadCountResponse(BaseModel):
    unread_count: int

class NotificationBroadcastRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Push notification headline")
    message: str = Field(..., min_length=1, max_length=1000, description="Notification body content")
    type: NotificationType = Field(NotificationType.SYSTEM, description="Category of notification")
    topic: Optional[str] = Field(None, description="Optional topic target (e.g. daily_wallpaper, new_wallpapers, all)")
    target_user_id: Optional[uuid.UUID] = Field(None, description="Optional single user destination")
    target_device_token: Optional[str] = Field(None, description="Optional direct FCM token destination")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom deep-linking payload data")
    save_to_inbox: bool = Field(True, description="Whether to persist in user's in-app notification inbox")

class NotificationBroadcastResult(BaseModel):
    success: bool
    sent_count: int
    failure_count: int
    message: str
    delivery_mode: str
