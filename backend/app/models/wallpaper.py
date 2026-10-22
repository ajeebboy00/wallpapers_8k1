import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.tag import wallpaper_tags

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.tag import Tag
    from app.models.favorite import Favorite
    from app.models.download import Download
    from app.models.view import WallpaperView
    from app.models.share import WallpaperShare
    from app.models.collection import CollectionWallpaper
    from app.models.report import Report

class Wallpaper(Base, TimestampMixin):
    __tablename__ = "wallpapers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Multi-variant image URLs
    original_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    preview_url: Mapped[str] = mapped_column(String(1024), nullable=False)

    # Image metadata
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    aspect_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_format: Mapped[str] = mapped_column(String(10), nullable=False)
    resolution: Mapped[str] = mapped_column(String(20), nullable=False)  # 8K, 4K, etc.

    # Foreign keys
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        index=True,
        nullable=False
    )
    uploader_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )

    # Metrics & Counter caches
    view_count: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    favorite_count: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    share_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Flags & Discovery
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_trending: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_daily: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    trending_score: Mapped[float] = mapped_column(Float, default=0.0, index=True, nullable=False)

    # AI Discovery, Visual Search & Similarity (Stage 15)
    dominant_color: Mapped[Optional[str]] = mapped_column(String(7), index=True, nullable=True)
    color_palette: Mapped[Optional[List[str]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True
    )
    perceptual_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    ai_tags: Mapped[Optional[List[str]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True
    )
    ai_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)

    # Relationships
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="wallpapers"
    )
    uploader: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="wallpapers",
        foreign_keys=[uploader_id]
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=wallpaper_tags,
        back_populates="wallpapers"
    )
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite",
        back_populates="wallpaper",
        cascade="all, delete-orphan"
    )
    downloads: Mapped[List["Download"]] = relationship(
        "Download",
        back_populates="wallpaper",
        cascade="all, delete-orphan"
    )
    views: Mapped[List["WallpaperView"]] = relationship(
        "WallpaperView",
        back_populates="wallpaper",
        cascade="all, delete-orphan"
    )
    shares: Mapped[List["WallpaperShare"]] = relationship(
        "WallpaperShare",
        back_populates="wallpaper",
        cascade="all, delete-orphan"
    )
    collection_entries: Mapped[List["CollectionWallpaper"]] = relationship(
        "CollectionWallpaper",
        back_populates="wallpaper",
        cascade="all, delete-orphan"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="wallpaper",
        cascade="all, delete-orphan"
    )

# Composite indexes for high-frequency queries
Index("ix_wallpapers_published_trending", Wallpaper.is_published, Wallpaper.is_trending, Wallpaper.trending_score.desc())
Index("ix_wallpapers_published_featured", Wallpaper.is_published, Wallpaper.is_featured, Wallpaper.created_at.desc())
Index("ix_wallpapers_published_daily", Wallpaper.is_published, Wallpaper.is_daily)
Index("ix_wallpapers_category_published", Wallpaper.category_id, Wallpaper.is_published, Wallpaper.created_at.desc())
