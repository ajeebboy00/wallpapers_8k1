import uuid
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    PaginationParams,
    get_current_user,
    get_db,
    get_optional_user,
    require_admin,
)
from app.models.user import User
from app.schemas.common import PaginatedResponse, StandardResponse
from app.schemas.notification import (
    DeviceTokenCreate,
    DeviceTokenResponse,
    NotificationBroadcastRequest,
    NotificationBroadcastResult,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post(
    "/devices",
    response_model=StandardResponse[DeviceTokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Register or update FCM device push token"
)
async def register_device(
    payload: DeviceTokenCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    user_id = current_user.id if current_user else None
    device = await service.register_device_token(payload=payload, user_id=user_id)
    return StandardResponse(
        success=True,
        data=device,
        message="Device token registered successfully"
    )

@router.delete(
    "/devices/{token}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Unregister FCM device push token"
)
async def unregister_device(
    token: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    user_id = current_user.id if current_user else None
    unregistered = await service.unregister_device_token(token=token, user_id=user_id)
    return StandardResponse(
        success=True,
        data={"unregistered": unregistered},
        message="Device token unregistered" if unregistered else "Device token not found"
    )

@router.get(
    "",
    response_model=PaginatedResponse[NotificationResponse],
    status_code=status.HTTP_200_OK,
    summary="List in-app notifications for authenticated user"
)
async def list_notifications(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    return await service.list_user_notifications(
        user_id=current_user.id,
        page=pagination.page,
        limit=pagination.limit
    )

@router.get(
    "/unread-count",
    response_model=StandardResponse[NotificationUnreadCountResponse],
    status_code=status.HTTP_200_OK,
    summary="Get count of unread in-app notifications"
)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    count = await service.get_unread_count(user_id=current_user.id)
    return StandardResponse(
        success=True,
        data=NotificationUnreadCountResponse(unread_count=count),
        message="Unread notification count retrieved"
    )

@router.patch(
    "/{notification_id}/read",
    response_model=StandardResponse[NotificationResponse],
    status_code=status.HTTP_200_OK,
    summary="Mark specific notification as read"
)
async def mark_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    notif = await service.mark_as_read(notification_id=notification_id, user_id=current_user.id)
    return StandardResponse(
        success=True,
        data=notif,
        message="Notification marked as read"
    )

@router.patch(
    "/read-all",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Mark all user notifications as read"
)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    updated_count = await service.mark_all_as_read(user_id=current_user.id)
    return StandardResponse(
        success=True,
        data={"updated_count": updated_count},
        message=f"{updated_count} notifications marked as read"
    )

@router.delete(
    "/{notification_id}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete in-app notification from inbox"
)
async def delete_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    deleted = await service.delete_notification(notification_id=notification_id, user_id=current_user.id)
    return StandardResponse(
        success=True,
        data={"deleted": deleted},
        message="Notification removed from inbox" if deleted else "Notification not found"
    )

# Administrative Broadcast Endpoints
@router.post(
    "/admin/broadcast",
    response_model=StandardResponse[NotificationBroadcastResult],
    status_code=status.HTTP_200_OK,
    summary="Broadcast push notification to devices and topics (Admin only)",
    dependencies=[Depends(require_admin)]
)
async def broadcast_notification(
    payload: NotificationBroadcastRequest,
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    result = await service.broadcast_notification(request=payload)
    return StandardResponse(
        success=result.success,
        data=result,
        message=result.message
    )

@router.post(
    "/admin/daily-spotlight",
    response_model=StandardResponse[NotificationBroadcastResult],
    status_code=status.HTTP_200_OK,
    summary="Trigger daily wallpaper push alert to subscribers (Admin only)",
    dependencies=[Depends(require_admin)]
)
async def trigger_daily_spotlight(
    wallpaper_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    result = await service.dispatch_daily_wallpaper_notification(wallpaper_id=wallpaper_id)
    return StandardResponse(
        success=result.success,
        data=result,
        message=result.message
    )
