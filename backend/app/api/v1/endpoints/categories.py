import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db, require_admin
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.common import PaginatedResponse, StandardResponse
from app.schemas.wallpaper import WallpaperFilterParams, WallpaperResponse
from app.services.category_service import CategoryService
from app.services.wallpaper_service import WallpaperService

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get(
    "",
    response_model=StandardResponse[List[CategoryResponse]],
    status_code=status.HTTP_200_OK,
    summary="List all categories"
)
async def list_categories(
    active_only: bool = Query(True, description="Filter for active categories only"),
    db: AsyncSession = Depends(get_db)
):
    service = CategoryService(db)
    categories = await service.list_categories(active_only=active_only)
    return StandardResponse(
        success=True,
        data=categories,
        message="Categories retrieved successfully"
    )

@router.get(
    "/{slug}",
    response_model=StandardResponse[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get category details by slug"
)
async def get_category(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    service = CategoryService(db)
    category = await service.get_by_slug(slug)
    return StandardResponse(
        success=True,
        data=category,
        message="Category details retrieved"
    )

@router.get(
    "/{slug}/wallpapers",
    response_model=PaginatedResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="List published wallpapers in category"
)
async def get_category_wallpapers(
    slug: str,
    pagination: PaginationParams = Depends(),
    sort: Optional[str] = Query("newest", pattern="^(newest|oldest|popular|downloads|views|favorites|trending)$"),
    db: AsyncSession = Depends(get_db)
):
    service = WallpaperService(db)
    filters = WallpaperFilterParams(
        category_slug=slug,
        is_published=True,
        sort=sort,
        order=pagination.order
    )
    return await service.list_wallpapers(filters, page=pagination.page, limit=pagination.limit)

@router.post(
    "",
    response_model=StandardResponse[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create new category (Admin only)"
)
async def create_category(
    payload: CategoryCreate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CategoryService(db)
    category = await service.create_category(payload)
    return StandardResponse(
        success=True,
        data=category,
        message="Category created successfully"
    )

@router.put(
    "/{category_id}",
    response_model=StandardResponse[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Update category (Admin only)"
)
async def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CategoryService(db)
    updated = await service.update_category(category_id, payload)
    return StandardResponse(
        success=True,
        data=updated,
        message="Category updated successfully"
    )

@router.delete(
    "/{category_id}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete category (Admin only)"
)
async def delete_category(
    category_id: uuid.UUID,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CategoryService(db)
    await service.delete_category(category_id)
    return StandardResponse(
        success=True,
        data={"deleted": True, "category_id": str(category_id)},
        message="Category deleted successfully"
    )
