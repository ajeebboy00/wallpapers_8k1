import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.wallpaper import WallpaperResponse

class SearchFilterParams(BaseModel):
    q: Optional[str] = Field(None, min_length=1, max_length=100, description="Search keyword / phrase")
    category: Optional[str] = Field(None, description="Category slug or UUID")
    tag: Optional[str] = Field(None, description="Tag slug or name")
    resolution: Optional[str] = Field(None, description="Filter resolution: 8K, 4K, 2K, FHD")
    color: Optional[str] = Field(None, description="Dominant hex color (e.g. #8B5CF6 or 8B5CF6) or name (e.g. purple, cyan, red)")
    color_tolerance: int = Field(50, ge=10, le=150, description="Color match distance tolerance in RGB space")
    is_premium: Optional[bool] = Field(None, description="Filter free vs premium wallpapers")
    is_ai_generated: Optional[bool] = Field(None, description="Filter AI generated wallpapers")
    orientation: Optional[str] = Field(
        None,
        pattern="^(portrait|landscape|square)$",
        description="Orientation filter based on image aspect ratio"
    )
    sort: str = Field(
        "relevance",
        pattern="^(relevance|newest|oldest|popular|downloads|views|favorites|trending)$",
        description="Sorting criteria"
    )
    order: str = Field("desc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(20, ge=1, le=100, description="Items per page")

class SearchSuggestionsResponse(BaseModel):
    query: Optional[str] = None
    popular_searches: List[str] = Field(default_factory=list)
    suggested_tags: List[str] = Field(default_factory=list)
    suggested_categories: List[str] = Field(default_factory=list)

class SimilarWallpaperItem(BaseModel):
    wallpaper: WallpaperResponse
    similarity_score: float = Field(..., description="Overall similarity score 0.0 - 1.0")
    matching_factors: List[str] = Field(default_factory=list, description="Factors contributing to match")

class SimilarWallpapersResponse(BaseModel):
    source_wallpaper_id: uuid.UUID
    similar: List[SimilarWallpaperItem] = Field(default_factory=list)

class AITaggingBatchRequest(BaseModel):
    wallpaper_id: Optional[uuid.UUID] = Field(None, description="Specific wallpaper to process, or None for batch")
    limit: int = Field(50, ge=1, le=500, description="Batch size of un-tagged wallpapers to analyze")
    force_reprocess: bool = Field(False, description="Whether to reprocess already tagged items")

class AITaggingBatchResponse(BaseModel):
    processed_count: int
    updated_wallpapers: List[WallpaperResponse] = Field(default_factory=list)
    message: str

class ColorStat(BaseModel):
    name: str
    hex: str
    count: int

class SearchAnalyticsResponse(BaseModel):
    total_wallpapers: int
    ai_indexed_wallpapers: int
    color_distribution: List[ColorStat] = Field(default_factory=list)
    popular_searches: List[str] = Field(default_factory=list)
