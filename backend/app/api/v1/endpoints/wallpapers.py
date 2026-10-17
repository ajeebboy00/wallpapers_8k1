import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db, require_admin
from app.models.user import User
from app.schemas.common import PaginatedResponse, StandardResponse
from app.schemas.wallpaper import (
    WallpaperCreate,
    WallpaperFilterParams,
    WallpaperResponse,
    WallpaperUpdate,
)
from app.services.upload_service import UploadService
from app.services.wallpaper_service import WallpaperService

router = APIRouter(prefix="/wallpapers", tags=["Wallpapers"])

@router.post(
    "/upload",
    response_model=StandardResponse[WallpaperResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload image file and create wallpaper in 1 step (Admin only)"
)
async def upload_and_create_wallpaper(
    file: UploadFile = File(..., description="Raw image file (JPEG, PNG, WEBP)"),
    title: str = Form(..., min_length=2, max_length=200),
    category_id: uuid.UUID = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None, description="Comma-separated tag names"),
    is_featured: bool = Form(False),
    is_trending: bool = Form(False),
    is_daily: bool = Form(False),
    is_published: bool = Form(True),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    file_bytes = await file.read()
    service = UploadService(db)
    created = await service.upload_and_create_wallpaper(
        file_bytes=file_bytes,
        filename=file.filename or "wallpaper.jpg",
        title=title,
        category_id=category_id,
        uploader_id=current_admin.id,
        description=description,
        tags=tag_list,
        is_featured=is_featured,
        is_trending=is_trending,
        is_daily=is_daily,
        is_published=is_published
    )
    return StandardResponse(
        success=True,
        data=created,
        message="Wallpaper uploaded and created successfully"
    )

@router.get(
    "",
    response_model=PaginatedResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="Browse and filter wallpapers"
)
async def list_wallpapers(
    pagination: PaginationParams = Depends(),
    category: Optional[str] = Query(None, description="Category slug"),
    tag: Optional[str] = Query(None, description="Tag slug"),
    resolution: Optional[str] = Query(None, description="Resolution filter: 8K, 4K, 2K, FHD"),
    is_featured: Optional[bool] = Query(None, description="Filter featured wallpapers"),
    is_trending: Optional[bool] = Query(None, description="Filter trending wallpapers"),
    is_daily: Optional[bool] = Query(None, description="Filter daily wallpapers"),
    sort: Optional[str] = Query("newest", pattern="^(newest|oldest|popular|downloads|views|favorites|trending)$"),
    db: AsyncSession = Depends(get_db)
):
    service = WallpaperService(db)
    filters = WallpaperFilterParams(
        category_slug=category,
        tag_slug=tag,
        resolution=resolution,
        is_featured=is_featured,
        is_trending=is_trending,
        is_daily=is_daily,
        is_published=True,
        sort=sort,
        order=pagination.order
    )
    return await service.list_wallpapers(filters, page=pagination.page, limit=pagination.limit)

@router.get(
    "/daily",
    response_model=StandardResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="Get today's daily wallpaper"
)
async def get_daily_wallpaper(
    db: AsyncSession = Depends(get_db)
):
    service = WallpaperService(db)
    daily = await service.get_daily_wallpaper()
    return StandardResponse(
        success=True,
        data=daily,
        message="Daily wallpaper retrieved"
    )

@router.get(
    "/{id_or_slug}",
    response_model=StandardResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="Get single wallpaper by ID or slug"
)
async def get_wallpaper(
    id_or_slug: str,
    db: AsyncSession = Depends(get_db)
):
    service = WallpaperService(db)
    wallpaper = await service.get_by_id_or_slug(id_or_slug)
    return StandardResponse(
        success=True,
        data=wallpaper,
        message="Wallpaper details retrieved"
    )

@router.get(
    "/{id_or_slug}/related",
    response_model=StandardResponse[List[WallpaperResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get related wallpapers"
)
async def get_related_wallpapers(
    id_or_slug: str,
    limit: int = Query(10, ge=1, le=50, description="Max related items to return"),
    db: AsyncSession = Depends(get_db)
):
    service = WallpaperService(db)
    related = await service.get_related_wallpapers(id_or_slug, limit=limit)
    return StandardResponse(
        success=True,
        data=related,
        message="Related wallpapers retrieved"
    )

@router.get(
    "/{id_or_slug}/similar",
    response_model=StandardResponse[List[WallpaperResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get visually & semantically similar wallpapers"
)
async def get_similar_wallpapers(
    id_or_slug: str,
    limit: int = Query(10, ge=1, le=50, description="Max similar items to return"),
    db: AsyncSession = Depends(get_db)
):
    from app.services.search_service import SearchService
    service = WallpaperService(db)
    wallpaper = await service.get_by_id_or_slug(id_or_slug)
    search_service = SearchService(db)
    similar_res = await search_service.get_similar_wallpapers(wallpaper_id=wallpaper.id, limit=limit)
    return StandardResponse(
        success=True,
        data=[item.wallpaper for item in similar_res.similar],
        message="Similar wallpapers retrieved"
    )

@router.post(
    "",
    response_model=StandardResponse[WallpaperResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create wallpaper record (Admin only)"
)
async def create_wallpaper(
    payload: WallpaperCreate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = WallpaperService(db)
    created = await service.create_wallpaper(payload, uploader_id=current_admin.id)
    return StandardResponse(
        success=True,
        data=created,
        message="Wallpaper created successfully"
    )

@router.put(
    "/{wallpaper_id}",
    response_model=StandardResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="Update wallpaper metadata (Admin only)"
)
async def update_wallpaper(
    wallpaper_id: uuid.UUID,
    payload: WallpaperUpdate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = WallpaperService(db)
    updated = await service.update_wallpaper(wallpaper_id, payload)
    return StandardResponse(
        success=True,
        data=updated,
        message="Wallpaper updated successfully"
    )

@router.delete(
    "/{wallpaper_id}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete wallpaper (Admin only)"
)
async def delete_wallpaper(
    wallpaper_id: uuid.UUID,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = WallpaperService(db)
    await service.delete_wallpaper(wallpaper_id)
    return StandardResponse(
        success=True,
        data={"deleted": True, "wallpaper_id": str(wallpaper_id)},
        message="Wallpaper deleted successfully"
    )
