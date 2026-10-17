import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, Enum, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import UserRole
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.wallpaper import Wallpaper
    from app.models.favorite import Favorite
    from app.models.download import Download
    from app.models.report import Report
    from app.models.notification import Notification, NotificationPreference
    from app.models.device_token import DeviceToken
    from app.models.subscription import Subscription
    from app.models.audit_log import AuditLog
    from app.models.refresh_token import RefreshToken

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum", native_enum=False),
        default=UserRole.USER,
        index=True,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    wallpapers: Mapped[List["Wallpaper"]] = relationship(
        "Wallpaper",
        back_populates="uploader",
        foreign_keys="Wallpaper.uploader_id"
    )
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    downloads: Mapped[List["Download"]] = relationship(
        "Download",
        back_populates="user"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="user",
        foreign_keys="Report.user_id"
    )
    reviewed_reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="reviewer",
        foreign_keys="Report.reviewed_by"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notification_preferences: Mapped[Optional["NotificationPreference"]] = relationship(
        "NotificationPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    device_tokens: Mapped[List["DeviceToken"]] = relationship(
        "DeviceToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )
