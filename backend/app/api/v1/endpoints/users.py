from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.user import (
    ChangePasswordRequest,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    UserProfileDetailResponse,
    UserUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/me",
    response_model=StandardResponse[UserProfileDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user's extended profile"
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    profile = await service.get_profile(current_user)
    return StandardResponse(
        success=True,
        data=profile,
        message="Profile retrieved successfully"
    )

@router.put(
    "/me",
    response_model=StandardResponse[UserProfileDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Update authenticated user's profile details"
)
async def update_my_profile(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    updated = await service.update_profile(current_user, payload)
    return StandardResponse(
        success=True,
        data=updated,
        message="Profile updated successfully"
    )

@router.put(
    "/me/password",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Change user password"
)
async def change_my_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    await service.change_password(current_user, payload)
    return StandardResponse(
        success=True,
        data={"updated": True},
        message="Password changed successfully"
    )

@router.get(
    "/me/notification-preferences",
    response_model=StandardResponse[NotificationPreferenceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user's notification preferences"
)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    prefs = await service.get_notification_preferences(current_user.id)
    return StandardResponse(
        success=True,
        data=prefs,
        message="Notification preferences retrieved"
    )

@router.put(
    "/me/notification-preferences",
    response_model=StandardResponse[NotificationPreferenceResponse],
    status_code=status.HTTP_200_OK,
    summary="Update user's notification preferences"
)
async def update_notification_preferences(
    payload: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    prefs = await service.update_notification_preferences(current_user.id, payload)
    return StandardResponse(
        success=True,
        data=prefs,
        message="Notification preferences updated"
    )
