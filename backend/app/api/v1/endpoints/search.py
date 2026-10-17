import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models.user import User
from app.schemas.common import PaginatedResponse, StandardResponse
from app.schemas.search import (
    AITaggingBatchRequest,
    AITaggingBatchResponse,
    SearchAnalyticsResponse,
    SearchFilterParams,
    SearchSuggestionsResponse,
    SimilarWallpapersResponse,
)
from app.schemas.wallpaper import WallpaperResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])

@router.get(
    "",
    response_model=PaginatedResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="Advanced search wallpapers with full-text, trigram fuzzy, color, and metadata filters"
)
async def search_wallpapers(
    q: Optional[str] = Query(None, min_length=1, max_length=100, description="Keyword / query string"),
    category: Optional[str] = Query(None, description="Category slug or UUID"),
    tag: Optional[str] = Query(None, description="Tag slug or name"),
    resolution: Optional[str] = Query(None, description="Resolution: 8K, 4K, 2K, FHD"),
    color: Optional[str] = Query(None, description="Hex color (e.g. #8B5CF6) or preset name (e.g. purple, cyan, dark)"),
    color_tolerance: int = Query(50, ge=10, le=150, description="RGB distance tolerance for color matching"),
    is_premium: Optional[bool] = Query(None, description="Filter free vs premium VIP wallpapers"),
    is_ai_generated: Optional[bool] = Query(None, description="Filter AI generated wallpapers"),
    orientation: Optional[str] = Query(None, pattern="^(portrait|landscape|square)$", description="Image orientation"),
    sort: str = Query("relevance", pattern="^(relevance|newest|oldest|popular|downloads|views|favorites|trending)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Advanced search engine endpoint supporting:
    - Trigram typo-tolerant fuzzy matching (pg_trgm) across title, description, and AI tags
    - Dominant color and color palette proximity filtering
    - Metadata filters: Category, Tag, Resolution, Orientation, is_premium, is_ai_generated
    - Dynamic sorting: Relevance, Popularity, Views, Downloads, Newest, Trending
    - Complete pagination metadata envelope
    """
    params = SearchFilterParams(
        q=q,
        category=category,
        tag=tag,
        resolution=resolution,
        color=color,
        color_tolerance=color_tolerance,
        is_premium=is_premium,
        is_ai_generated=is_ai_generated,
        orientation=orientation,
        sort=sort,
        order=order,
        page=page,
        limit=limit
    )
    service = SearchService(db)
    return await service.search_wallpapers(params)

@router.get(
    "/similar/{wallpaper_id}",
    response_model=StandardResponse[SimilarWallpapersResponse],
    status_code=status.HTTP_200_OK,
    summary="Find visually & semantically similar wallpapers"
)
async def get_similar_wallpapers(
    wallpaper_id: uuid.UUID,
    limit: int = Query(10, ge=1, le=30, description="Max similar items to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Finds visually and semantically similar wallpapers using multi-factor AI scoring:
    - Color palette proximity & dominant hue distance
    - Tag & semantic embedding overlap (Jaccard similarity)
    - Perceptual hash Hamming distance (visual layout similarity)
    - Category & resolution affinity
    """
    service = SearchService(db)
    similar_data = await service.get_similar_wallpapers(wallpaper_id=wallpaper_id, limit=limit)
    return StandardResponse(
        success=True,
        data=similar_data,
        message=f"Found {len(similar_data.similar)} similar wallpapers",
    )

@router.post(
    "/ai/tag-batch",
    response_model=StandardResponse[AITaggingBatchResponse],
    status_code=status.HTTP_200_OK,
    summary="Batch AI vision tagging & color extraction (Admin only)"
)
async def batch_ai_tagging(
    payload: AITaggingBatchRequest,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin pipeline trigger to analyze wallpapers and extract dominant color,
    color palette, perceptual visual hash, AI semantic tags, and AI descriptions.
    """
    service = SearchService(db)
    result = await service.run_batch_ai_tagging(
        limit=payload.limit,
        force_reprocess=payload.force_reprocess,
        wallpaper_id=payload.wallpaper_id,
    )
    return StandardResponse(
        success=True,
        data=result,
        message=result.message,
    )

@router.get(
    "/analytics",
    response_model=StandardResponse[SearchAnalyticsResponse],
    status_code=status.HTTP_200_OK,
    summary="Search, index, and color distribution analytics"
)
async def get_search_analytics(
    db: AsyncSession = Depends(get_db)
):
    """Returns platform search health, dominant color distribution, and AI index coverage."""
    service = SearchService(db)
    analytics = await service.get_search_analytics()
    return StandardResponse(
        success=True,
        data=analytics,
        message="Search analytics retrieved successfully",
    )

@router.get(
    "/suggestions",
    response_model=StandardResponse[SearchSuggestionsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get search suggestions and popular search tags"
)
async def get_search_suggestions(
    q: Optional[str] = Query(None, max_length=50, description="Optional search prefix for auto-complete"),
    limit: int = Query(10, ge=1, le=50, description="Max suggestions to return"),
    db: AsyncSession = Depends(get_db)
):
    """Returns curated popular search terms, trending tags, and category keywords."""
    service = SearchService(db)
    suggestions = await service.get_suggestions(query=q, limit=limit)
    return StandardResponse(
        success=True,
        data=suggestions,
        message="Search suggestions retrieved"
    )
