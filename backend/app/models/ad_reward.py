import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.wallpaper import Wallpaper

class AdRewardUnlock(Base):
    __tablename__ = "ad_reward_unlocks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    wallpaper_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("wallpapers.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    device_id: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    reward_type: Mapped[str] = mapped_column(String(50), default="wallpaper_download", nullable=False)
    ad_network: Mapped[str] = mapped_column(String(50), default="admob", nullable=False)
    ad_unit_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    transaction_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User")
    wallpaper: Mapped["Wallpaper"] = relationship("Wallpaper")
