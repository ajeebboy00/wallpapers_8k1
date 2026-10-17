import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.wallpaper import WallpaperResponse

class CollectionBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    cover_image_url: Optional[str] = Field(None, max_length=1024)
    is_featured: bool = False
    is_published: bool = True

class CollectionCreate(CollectionBase):
    slug: Optional[str] = Field(None, max_length=100)
    wallpaper_ids: Optional[List[uuid.UUID]] = Field(default_factory=list)

class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    cover_image_url: Optional[str] = Field(None, max_length=1024)
    is_featured: Optional[bool] = None
    is_published: Optional[bool] = None
    wallpaper_ids: Optional[List[uuid.UUID]] = None

class CollectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_featured: bool
    is_published: bool
    wallpaper_count: int = 0
    created_at: datetime
    updated_at: datetime

class CollectionDetailResponse(CollectionResponse):
    wallpapers: List[WallpaperResponse] = Field(default_factory=list)
