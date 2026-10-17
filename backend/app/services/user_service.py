import uuid
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.core.security import get_password_hash, verify_password
from app.models.download import Download
from app.models.favorite import Favorite
from app.models.notification import NotificationPreference
from app.models.user import User
from app.schemas.user import (
    ChangePasswordRequest,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    UserProfileDetailResponse,
    UserUpdateRequest,
)

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_profile(self, user: User) -> UserProfileDetailResponse:
        # Count favorites
        fav_count_stmt = select(func.count(Favorite.id)).where(Favorite.user_id == user.id)
        fav_count = (await self.session.execute(fav_count_stmt)).scalar() or 0

        # Count downloads
        dl_count_stmt = select(func.count(func.distinct(Download.wallpaper_id))).where(Download.user_id == user.id)
        dl_count = (await self.session.execute(dl_count_stmt)).scalar() or 0

        data = UserProfileDetailResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            email_verified=user.email_verified,
            profile_image_url=user.profile_image_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
            favorites_count=fav_count,
            downloads_count=dl_count,
        )
        return data

    async def update_profile(self, user: User, payload: UserUpdateRequest) -> UserProfileDetailResponse:
        if payload.name is not None:
            user.name = payload.name.strip()
        if payload.profile_image_url is not None:
            user.profile_image_url = payload.profile_image_url.strip()

        await self.session.commit()
        await self.session.refresh(user)
        return await self.get_profile(user)

    async def change_password(self, user: User, payload: ChangePasswordRequest) -> bool:
        if not verify_password(payload.current_password, user.password_hash):
            raise UnauthorizedException("Current password is incorrect", code="INVALID_CURRENT_PASSWORD")

        if payload.current_password == payload.new_password:
            raise BadRequestException("New password cannot be identical to current password")

        user.password_hash = get_password_hash(payload.new_password)
        await self.session.commit()
        return True

    async def get_notification_preferences(self, user_id: uuid.UUID) -> NotificationPreferenceResponse:
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await self.session.execute(stmt)
        pref = result.scalar_one_or_none()

        if not pref:
            pref = NotificationPreference(user_id=user_id)
            self.session.add(pref)
            await self.session.commit()
            await self.session.refresh(pref)

        return NotificationPreferenceResponse.model_validate(pref)

    async def update_notification_preferences(
        self,
        user_id: uuid.UUID,
        payload: NotificationPreferenceUpdate
    ) -> NotificationPreferenceResponse:
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await self.session.execute(stmt)
        pref = result.scalar_one_or_none()

        if not pref:
            pref = NotificationPreference(user_id=user_id)
            self.session.add(pref)

        if payload.daily_wallpaper is not None:
            pref.daily_wallpaper = payload.daily_wallpaper
        if payload.new_wallpapers is not None:
            pref.new_wallpapers = payload.new_wallpapers
        if payload.new_collections is not None:
            pref.new_collections = payload.new_collections
        if payload.featured is not None:
            pref.featured = payload.featured
        if payload.promotional is not None:
            pref.promotional = payload.promotional

        await self.session.commit()
        await self.session.refresh(pref)
        return NotificationPreferenceResponse.model_validate(pref)
