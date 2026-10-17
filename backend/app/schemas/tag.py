import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TagBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Unique tag name")

class TagCreate(TagBase):
    slug: Optional[str] = Field(None, max_length=50, description="Custom slug or auto-generated")

class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime
