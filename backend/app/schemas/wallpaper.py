import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse

class CategorySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str

class WallpaperBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None)
    category_id: uuid.UUID
    original_url: str = Field(..., max_length=1024)
    image_url: str = Field(..., max_length=1024)
    thumbnail_url: str = Field(..., max_length=1024)
    preview_url: str = Field(..., max_length=1024)
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)
    file_size: int = Field(..., gt=0)
    file_format: str = Field(..., max_length=10)
    resolution: str = Field(..., max_length=20)
    is_featured: bool = False
    is_trending: bool = False
    is_daily: bool = False
    is_premium: bool = False
    dominant_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    perceptual_hash: Optional[str] = None
    ai_tags: Optional[List[str]] = None
    ai_description: Optional[str] = None
    is_ai_generated: bool = False
    is_published: bool = True

class WallpaperCreate(WallpaperBase):
    slug: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = Field(default_factory=list, description="List of tag names")

class WallpaperUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    slug: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    original_url: Optional[str] = Field(None, max_length=1024)
    image_url: Optional[str] = Field(None, max_length=1024)
    thumbnail_url: Optional[str] = Field(None, max_length=1024)
    preview_url: Optional[str] = Field(None, max_length=1024)
    width: Optional[int] = Field(None, gt=0)
    height: Optional[int] = Field(None, gt=0)
    file_size: Optional[int] = Field(None, gt=0)
    file_format: Optional[str] = Field(None, max_length=10)
    resolution: Optional[str] = Field(None, max_length=20)
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_trending: Optional[bool] = None
    is_daily: Optional[bool] = None
    is_premium: Optional[bool] = None
    dominant_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    perceptual_hash: Optional[str] = None
    ai_tags: Optional[List[str]] = None
    ai_description: Optional[str] = None
    is_ai_generated: Optional[bool] = None
    is_published: Optional[bool] = None

class WallpaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    description: Optional[str] = None
    original_url: str
    image_url: str
    thumbnail_url: str
    preview_url: str
    width: int
    height: int
    aspect_ratio: float
    file_size: int
    file_format: str
    resolution: str
    category_id: uuid.UUID
    uploader_id: Optional[uuid.UUID] = None
    view_count: int
    download_count: int
    favorite_count: int
    share_count: int
    is_featured: bool
    is_trending: bool
    is_daily: bool
    is_premium: bool = False
    dominant_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    perceptual_hash: Optional[str] = None
    ai_tags: Optional[List[str]] = None
    ai_description: Optional[str] = None
    is_ai_generated: bool = False
    is_published: bool
    trending_score: float
    created_at: datetime
    updated_at: datetime
    category: Optional[CategorySummary] = None
    tags: List[TagResponse] = Field(default_factory=list)

class WallpaperFilterParams(BaseModel):
    category_slug: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    tag_slug: Optional[str] = None
    resolution: Optional[str] = None
    dominant_color: Optional[str] = None
    is_featured: Optional[bool] = None
    is_trending: Optional[bool] = None
    is_daily: Optional[bool] = None
    is_premium: Optional[bool] = None
    is_ai_generated: Optional[bool] = None
    is_published: Optional[bool] = True
    sort: Optional[str] = Field(
        "newest",
        pattern="^(newest|oldest|popular|downloads|views|favorites|trending)$",
        description="Sort by criteria"
    )
    order: str = Field("desc", pattern="^(asc|desc)$")
