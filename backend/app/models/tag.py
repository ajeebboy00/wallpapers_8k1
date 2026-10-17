import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.wallpaper import Wallpaper

# Association table for Wallpaper <-> Tag (Many-to-Many)
wallpaper_tags = Table(
    "wallpaper_tags",
    Base.metadata,
    Column("wallpaper_id", Uuid(as_uuid=True), ForeignKey("wallpapers.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Uuid(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    wallpapers: Mapped[List["Wallpaper"]] = relationship(
        "Wallpaper",
        secondary=wallpaper_tags,
        back_populates="tags"
    )
