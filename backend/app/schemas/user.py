import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.constants import UserRole

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100, description="Full name or display name")

class UserRegisterRequest(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="Minimum 8 characters")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    profile_image_url: Optional[str] = Field(None, max_length=1024)

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters long")
        return v

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8, max_length=128)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    email_verified: bool
    profile_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

class UserProfileDetailResponse(UserResponse):
    favorites_count: int = 0
    downloads_count: int = 0

class NotificationPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    daily_wallpaper: bool
    new_wallpapers: bool
    new_collections: bool
    featured: bool
    promotional: bool

class NotificationPreferenceUpdate(BaseModel):
    daily_wallpaper: Optional[bool] = None
    new_wallpapers: Optional[bool] = None
    new_collections: Optional[bool] = None
    featured: Optional[bool] = None
    promotional: Optional[bool] = None
