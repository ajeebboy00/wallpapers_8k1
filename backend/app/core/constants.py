from enum import Enum

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

class SubscriptionPlan(str, Enum):
    PRO_MONTHLY = "PRO_MONTHLY"
    PRO_ANNUAL = "PRO_ANNUAL"
    PRO_LIFETIME = "PRO_LIFETIME"

class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    GRACE_PERIOD = "GRACE_PERIOD"

class ReportStatus(str, Enum):
    PENDING = "PENDING"
    REVIEWING = "REVIEWING"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"

class ReportReason(str, Enum):
    COPYRIGHT = "COPYRIGHT"
    INAPPROPRIATE = "INAPPROPRIATE"
    SPAM = "SPAM"
    MISLEADING = "MISLEADING"
    OTHER = "OTHER"

class NotificationType(str, Enum):
    DAILY_WALLPAPER = "DAILY_WALLPAPER"
    NEW_WALLPAPER = "NEW_WALLPAPER"
    NEW_COLLECTION = "NEW_COLLECTION"
    FEATURED = "FEATURED"
    SYSTEM = "SYSTEM"
    PROMOTIONAL = "PROMOTIONAL"

class SharePlatform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    WHATSAPP = "whatsapp"
    X = "x"
    COPY_LINK = "copy_link"
    OTHER = "other"

class WallpaperResolution(str, Enum):
    RES_8K = "8K"
    RES_4K = "4K"
    RES_2K = "2K"
    RES_FHD = "FHD"

class AuditAction(str, Enum):
    WALLPAPER_CREATED = "WALLPAPER_CREATED"
    WALLPAPER_UPDATED = "WALLPAPER_UPDATED"
    WALLPAPER_DELETED = "WALLPAPER_DELETED"
    USER_DEACTIVATED = "USER_DEACTIVATED"
    ROLE_CHANGED = "ROLE_CHANGED"
    REPORT_RESOLVED = "REPORT_RESOLVED"
    SETTINGS_UPDATED = "SETTINGS_UPDATED"

# File constraints
MAX_IMAGE_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_MIME_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/webp": [".webp"]
}
