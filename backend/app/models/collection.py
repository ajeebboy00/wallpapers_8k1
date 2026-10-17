import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.wallpaper import Wallpaper

class CollectionWallpaper(Base):
    __tablename__ = "collection_wallpapers"

    collection_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True
    )
    wallpaper_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("wallpapers.id", ondelete="CASCADE"),
        primary_key=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)

    # Relationships
    collection: Mapped["Collection"] = relationship("Collection", back_populates="wallpapers")
    wallpaper: Mapped["Wallpaper"] = relationship("Wallpaper", back_populates="collection_entries")

class Collection(Base, TimestampMixin):
    __tablename__ = "collections"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)

    # Relationships
    wallpapers: Mapped[List["CollectionWallpaper"]] = relationship(
        "CollectionWallpaper",
        back_populates="collection",
        cascade="all, delete-orphan",
        order_by="CollectionWallpaper.sort_order"
    )
