import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Display name of category")
    description: Optional[str] = Field(None, description="Detailed category description")
    image_url: Optional[str] = Field(None, max_length=1024, description="Representative cover/thumbnail image URL")
    sort_order: int = Field(0, description="Display priority ordering")
    is_active: bool = Field(True, description="Whether category is publicly visible")

class CategoryCreate(CategoryBase):
    slug: Optional[str] = Field(None, max_length=100, description="Custom slug or auto-generated from name")

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=1024)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int
    is_active: bool
    wallpaper_count: int = 0
    created_at: datetime
    updated_at: datetime
