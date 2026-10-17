import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.models.notification import NotificationPreference
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
        email_verified: bool = False
    ) -> User:
        user = User(
            name=name.strip(),
            email=email.lower().strip(),
            password_hash=password_hash,
            role=role,
            is_active=is_active,
            email_verified=email_verified
        )
        self.session.add(user)
        await self.session.flush()

        # Initialize default notification preferences
        pref = NotificationPreference(
            user_id=user.id,
            daily_wallpaper=True,
            new_wallpapers=True,
            new_collections=True,
            featured=True,
            promotional=False
        )
        self.session.add(pref)
        await self.session.flush()

        return user

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)
        await self.session.flush()
