import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.wallpaper import Wallpaper

class WallpaperView(Base):
    __tablename__ = "wallpaper_views"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    wallpaper_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("wallpapers.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    session_identifier: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )

    # Relationships
    wallpaper: Mapped["Wallpaper"] = relationship("Wallpaper", back_populates="views")

# Composite index for deduplication checks
Index("ix_views_wallpaper_session_created", WallpaperView.wallpaper_id, WallpaperView.session_identifier, WallpaperView.created_at)
