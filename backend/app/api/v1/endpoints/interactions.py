import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_current_user, get_db, get_optional_user
from app.models.user import User
from app.schemas.common import PaginatedResponse, StandardResponse
from app.schemas.interaction import (
    DownloadRecordResponse,
    FavoriteStatusResponse,
    FavoriteToggleResponse,
    ReportCreateRequest,
    ReportResponse,
    ShareRecordRequest,
    ShareRecordResponse,
    ViewRecordRequest,
    ViewRecordResponse,
)
from app.schemas.wallpaper import WallpaperResponse
from app.services.interaction_service import InteractionService

router = APIRouter(tags=["Interactions"])

# 1. Favorite Actions
@router.post(
    "/wallpapers/{wallpaper_id}/favorite",
    response_model=StandardResponse[FavoriteToggleResponse],
    status_code=status.HTTP_200_OK,
    summary="Add wallpaper to user favorites"
)
async def add_favorite(
    wallpaper_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = InteractionService(db)
    result = await service.add_favorite(current_user.id, wallpaper_id)
    return StandardResponse(
        success=True,
        data=result,
        message="Wallpaper added to favorites"
    )

@router.delete(
    "/wallpapers/{wallpaper_id}/favorite",
    response_model=StandardResponse[FavoriteToggleResponse],
    status_code=status.HTTP_200_OK,
    summary="Remove wallpaper from user favorites"
)
async def remove_favorite(
    wallpaper_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = InteractionService(db)
    result = await service.remove_favorite(current_user.id, wallpaper_id)
    return StandardResponse(
        success=True,
        data=result,
        message="Wallpaper removed from favorites"
    )

@router.get(
    "/wallpapers/{wallpaper_id}/favorite",
    response_model=StandardResponse[FavoriteStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Check if wallpaper is favorited by current user"
)
async def check_favorite(
    wallpaper_id: uuid.UUID,
    user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    service = InteractionService(db)
    result = await service.check_favorite(user.id if user else None, wallpaper_id)
    return StandardResponse(
        success=True,
        data=result,
        message="Favorite status retrieved"
    )

# 2. Download Action
@router.post(
    "/wallpapers/{wallpaper_id}/download",
    response_model=StandardResponse[DownloadRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Record wallpaper download and retrieve direct download URL"
)
async def record_download(
    wallpaper_id: uuid.UUID,
    user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    service = InteractionService(db)
    result = await service.record_download(wallpaper_id, user_id=user.id if user else None)
    return StandardResponse(
        success=True,
        data=result,
        message="Download recorded"
    )

# 3. View Action
@router.post(
    "/wallpapers/{wallpaper_id}/view",
    response_model=StandardResponse[ViewRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Record wallpaper impression / view"
)
async def record_view(
    wallpaper_id: uuid.UUID,
    payload: Optional[ViewRecordRequest] = None,
    user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    service = InteractionService(db)
    result = await service.record_view(
        wallpaper_id=wallpaper_id,
        user_id=user.id if user else None,
        session_identifier=payload.session_identifier if payload else None
    )
    return StandardResponse(
        success=True,
        data=result,
        message="View recorded"
    )

# 4. Share Action
@router.post(
    "/wallpapers/{wallpaper_id}/share",
    response_model=StandardResponse[ShareRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Record wallpaper share"
)
async def record_share(
    wallpaper_id: uuid.UUID,
    payload: Optional[ShareRecordRequest] = None,
    user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    service = InteractionService(db)
    result = await service.record_share(
        wallpaper_id=wallpaper_id,
        user_id=user.id if user else None,
        platform=payload.platform if payload else None
    )
    return StandardResponse(
        success=True,
        data=result,
        message="Share recorded"
    )

# 5. Report Action
@router.post(
    "/wallpapers/{wallpaper_id}/report",
    response_model=StandardResponse[ReportResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Report wallpaper for inappropriate content or copyright"
)
async def report_wallpaper(
    wallpaper_id: uuid.UUID,
    payload: ReportCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = InteractionService(db)
    result = await service.create_report(
        user_id=current_user.id,
        wallpaper_id=wallpaper_id,
        reason=payload.reason,
        description=payload.description
    )
    return StandardResponse(
        success=True,
        data=result,
        message="Report submitted successfully"
    )

# 6. User History & Library
@router.get(
    "/users/me/favorites",
    response_model=PaginatedResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="Get wallpapers favorited by current user"
)
async def get_my_favorites(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = InteractionService(db)
    return await service.get_user_favorites(
        user_id=current_user.id,
        page=pagination.page,
        limit=pagination.limit
    )

@router.get(
    "/users/me/downloads",
    response_model=PaginatedResponse[WallpaperResponse],
    status_code=status.HTTP_200_OK,
    summary="Get wallpapers downloaded by current user"
)
async def get_my_downloads(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = InteractionService(db)
    return await service.get_user_downloads(
        user_id=current_user.id,
        page=pagination.page,
        limit=pagination.limit
    )
