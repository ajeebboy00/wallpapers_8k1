import math
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import NotificationType
from app.core.exceptions import NotFoundException
from app.models.device_token import DeviceToken
from app.models.notification import Notification, NotificationPreference
from app.models.wallpaper import Wallpaper
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.notification import (
    DeviceTokenCreate,
    DeviceTokenResponse,
    NotificationBroadcastRequest,
    NotificationBroadcastResult,
    NotificationResponse,
)
from app.services.fcm_service import fcm_service

class NotificationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_device_token(
        self,
        payload: DeviceTokenCreate,
        user_id: Optional[uuid.UUID] = None
    ) -> DeviceTokenResponse:
        """Register or update an FCM device token."""
        stmt = select(DeviceToken).where(DeviceToken.token == payload.token)
        device = (await self.session.execute(stmt)).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if device:
            if user_id is not None:
                device.user_id = user_id
            if payload.device_id:
                device.device_id = payload.device_id
            device.platform = payload.platform
            if payload.app_version:
                device.app_version = payload.app_version
            if payload.topics:
                # Merge topics
                current_topics = set(device.topics or [])
                current_topics.update(payload.topics)
                device.topics = list(current_topics)
            device.is_active = True
            device.last_seen_at = now
            device.updated_at = now
        else:
            device = DeviceToken(
                user_id=user_id,
                token=payload.token,
                device_id=payload.device_id,
                platform=payload.platform,
                app_version=payload.app_version,
                is_active=True,
                topics=payload.topics or ["daily_wallpaper", "new_wallpapers", "featured"],
                created_at=now,
                updated_at=now,
                last_seen_at=now
            )
            self.session.add(device)

        await self.session.commit()
        await self.session.refresh(device)
        return DeviceTokenResponse.model_validate(device)

    async def unregister_device_token(self, token: str, user_id: Optional[uuid.UUID] = None) -> bool:
        """Unregister or deactivate an FCM token."""
        query = select(DeviceToken).where(DeviceToken.token == token)
        if user_id:
            query = query.where(DeviceToken.user_id == user_id)

        device = (await self.session.execute(query)).scalar_one_or_none()
        if not device:
            return False

        device.is_active = False
        device.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True

    async def list_user_notifications(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        limit: int = 20
    ) -> PaginatedResponse[NotificationResponse]:
        """List in-app notifications for the user plus global system broadcasts."""
        query = select(Notification).where(
            or_(Notification.user_id == user_id, Notification.user_id.is_(None))
        )

        count_subq = query.subquery()
        total = (await self.session.execute(select(func.count()).select_from(count_subq))).scalar() or 0

        offset = (page - 1) * limit
        paginated_stmt = (
            query
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        items = list((await self.session.execute(paginated_stmt)).scalars().all())

        total_pages = math.ceil(total / limit) if total > 0 else 1
        meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        return PaginatedResponse(
            success=True,
            data=[NotificationResponse.model_validate(item) for item in items],
            meta=meta,
            message="Notifications retrieved"
        )

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        """Get the count of unread notifications for a user."""
        stmt = (
            select(func.count(Notification.id))
            .where(
                or_(Notification.user_id == user_id, Notification.user_id.is_(None)),
                Notification.is_read.is_(False)
            )
        )
        count = (await self.session.execute(stmt)).scalar() or 0
        return count

    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> NotificationResponse:
        """Mark a specific notification as read."""
        stmt = select(Notification).where(
            Notification.id == notification_id,
            or_(Notification.user_id == user_id, Notification.user_id.is_(None))
        )
        notif = (await self.session.execute(stmt)).scalar_one_or_none()
        if not notif:
            raise NotFoundException("Notification not found", code="NOTIFICATION_NOT_FOUND")

        notif.is_read = True
        await self.session.commit()
        await self.session.refresh(notif)
        return NotificationResponse.model_validate(notif)

    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        """Mark all notifications as read for this user."""
        stmt = (
            update(Notification)
            .where(
                or_(Notification.user_id == user_id, Notification.user_id.is_(None)),
                Notification.is_read.is_(False)
            )
            .values(is_read=True)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def delete_notification(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete an in-app notification from the user's inbox."""
        stmt = (
            delete(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def broadcast_notification(
        self,
        request: NotificationBroadcastRequest
    ) -> NotificationBroadcastResult:
        """Send push notification and optionally record in user inbox."""
        # 1. Save to in-app notification inbox if requested
        if request.save_to_inbox:
            inbox_item = Notification(
                user_id=request.target_user_id,  # None if broadcast to all
                title=request.title,
                message=request.message,
                type=request.type,
                data=request.data or {},
                is_read=False,
                created_at=datetime.now(timezone.utc)
            )
            self.session.add(inbox_item)
            await self.session.commit()

        # 2. Resolve destination FCM tokens
        target_tokens: List[str] = []

        if request.target_device_token:
            target_tokens = [request.target_device_token]
        elif request.target_user_id:
            # Query active tokens for target user
            token_stmt = select(DeviceToken.token).where(
                DeviceToken.user_id == request.target_user_id,
                DeviceToken.is_active.is_(True)
            )
            target_tokens = list((await self.session.execute(token_stmt)).scalars().all())
        else:
            # Broadcast to active tokens
            query = select(DeviceToken.token).where(DeviceToken.is_active.is_(True))
            target_tokens = list((await self.session.execute(query)).scalars().all())

        # 3. Dispatch via FCM push delivery service
        image_url = (request.data or {}).get("image_url") or (request.data or {}).get("thumbnail_url")
        delivery = await fcm_service.send_multicast(
            tokens=target_tokens,
            title=request.title,
            body=request.message,
            data=request.data,
            image_url=image_url
        )

        return NotificationBroadcastResult(
            success=delivery.success,
            sent_count=delivery.sent_count,
            failure_count=delivery.failure_count,
            message=delivery.message,
            delivery_mode=delivery.delivery_mode
        )

    async def dispatch_daily_wallpaper_notification(
        self,
        wallpaper_id: Optional[uuid.UUID] = None
    ) -> NotificationBroadcastResult:
        """Dispatch daily wallpaper alert for today's spotlight wallpaper."""
        wp = None
        if wallpaper_id:
            stmt = select(Wallpaper).where(Wallpaper.id == wallpaper_id)
            wp = (await self.session.execute(stmt)).scalar_one_or_none()
        else:
            stmt = (
                select(Wallpaper)
                .where(Wallpaper.is_daily.is_(True), Wallpaper.is_published.is_(True))
                .order_by(Wallpaper.created_at.desc())
            )
            wp = (await self.session.execute(stmt)).scalars().first()

        if not wp:
            raise NotFoundException("No active daily wallpaper found for spotlight notification", code="DAILY_WALLPAPER_NOT_FOUND")

        req = NotificationBroadcastRequest(
            title="Today's 8K Spotlight is Live! ✨",
            message=f"Discover '{wp.title}' — handpicked today in flawless 8K Ultra-HD.",
            type=NotificationType.DAILY_WALLPAPER,
            topic="daily_wallpaper",
            data={
                "wallpaper_id": str(wp.id),
                "image_url": wp.thumbnail_url,
                "target_screen": "wallpaper_details"
            },
            save_to_inbox=True
        )
        return await self.broadcast_notification(req)
