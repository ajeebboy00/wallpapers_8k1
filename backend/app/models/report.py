import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ReportReason, ReportStatus
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.wallpaper import Wallpaper

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    wallpaper_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("wallpapers.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    reason: Mapped[ReportReason] = mapped_column(
        Enum(ReportReason, name="report_reason_enum", native_enum=False),
        index=True,
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status_enum", native_enum=False),
        default=ReportStatus.PENDING,
        index=True,
        nullable=False
    )
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="reports"
    )
    wallpaper: Mapped["Wallpaper"] = relationship(
        "Wallpaper",
        back_populates="reports"
    )
    reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[reviewed_by],
        back_populates="reviewed_reports"
    )
