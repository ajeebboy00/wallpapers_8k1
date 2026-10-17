import asyncio
import json
from sqlalchemy import select

from app.core.config import settings
from app.core.constants import UserRole
from app.core.logging import logger
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models import AppSetting, Category, NotificationPreference, User

INITIAL_CATEGORIES = [
    {"name": "Black & Dark", "slug": "black-dark", "sort_order": 1, "description": "Ultra dark AMOLED wallpapers with deep blacks and high contrast."},
    {"name": "Nature", "slug": "nature", "sort_order": 2, "description": "Stunning landscapes, forests, rivers, and breathtaking wilderness in 8K."},
    {"name": "Cars", "slug": "cars", "sort_order": 3, "description": "Supercars, hypercars, classic automobiles, and motorsport aesthetics."},
    {"name": "Gaming", "slug": "gaming", "sort_order": 4, "description": "Iconic gaming environments, character art, and console/PC gaming visuals."},
    {"name": "Technology", "slug": "technology", "sort_order": 5, "description": "Futuristic tech, cyber aesthetics, microchips, and hardware design."},
    {"name": "Space", "slug": "space", "sort_order": 6, "description": "Deep space nebulae, galaxies, stars, exoplanets, and cosmos imagery."},
    {"name": "Mountains", "slug": "mountains", "sort_order": 7, "description": "Towering peaks, alpine vistas, snowy ranges, and mountain valleys."},
    {"name": "Ocean", "slug": "ocean", "sort_order": 8, "description": "Deep blue seas, crashing waves, coral reefs, and coastal waters."},
    {"name": "Minimal", "slug": "minimal", "sort_order": 9, "description": "Clean lines, subtle geometric shapes, and uncluttered negative space."},
    {"name": "Abstract", "slug": "abstract", "sort_order": 10, "description": "Fluid 3D art, vibrant color blends, and surreal creative concepts."},
]

INITIAL_APP_SETTINGS = [
    {
        "key": "social_links",
        "value": json.dumps({
            "instagram": "https://instagram.com/wallpapers_8k1",
            "tiktok": "https://tiktok.com/@wallpapers_8k1",
            "youtube": "https://youtube.com/@wallpapers_8k1",
            "pinterest": "https://pinterest.com/wallpapers_8k1",
            "x": "https://x.com/wallpapers_8k1"
        }),
        "description": "Official brand social media ecosystem links"
    },
    {
        "key": "platform_info",
        "value": json.dumps({
            "brand_name": "Wallpapers_8k1",
            "short_brand": "W8K1",
            "support_email": "support@wallpapers8k1.com",
            "copyright_notice": "Copyright © 2026 Wallpapers_8k1. All rights reserved."
        }),
        "description": "General platform metadata and legal identification"
    }
]

async def seed_development_data():
    """Seeds essential development categories, superadmin, and platform settings.
    Guarded against running in production.
    """
    if settings.APP_ENV == "production":
        logger.error("Seeding command aborted: Cannot run development seed in production!")
        return

    logger.info("==> Running development database seed...")

    async with AsyncSessionLocal() as session:
        # 1. Seed Categories
        for cat_data in INITIAL_CATEGORIES:
            stmt = select(Category).where(Category.slug == cat_data["slug"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                cat = Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    sort_order=cat_data["sort_order"],
                    description=cat_data["description"],
                    is_active=True
                )
                session.add(cat)
                logger.info(f"  + Added category: {cat_data['name']}")

        # 2. Seed Platform Settings
        for setting_data in INITIAL_APP_SETTINGS:
            stmt = select(AppSetting).where(AppSetting.key == setting_data["key"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                setting = AppSetting(
                    key=setting_data["key"],
                    value=setting_data["value"],
                    description=setting_data["description"]
                )
                session.add(setting)
                logger.info(f"  + Added setting: {setting_data['key']}")

        # 3. Seed Super Admin User
        stmt = select(User).where(User.email == settings.SUPERADMIN_EMAIL)
        result = await session.execute(stmt)
        existing_admin = result.scalar_one_or_none()
        if not existing_admin:
            hashed_pw = get_password_hash(settings.SUPERADMIN_PASSWORD)
            superadmin = User(
                name=settings.SUPERADMIN_NAME,
                email=settings.SUPERADMIN_EMAIL,
                password_hash=hashed_pw,
                role=UserRole.SUPER_ADMIN,
                is_active=True,
                email_verified=True
            )
            session.add(superadmin)
            await session.flush()

            # Create default notification preference for superadmin
            pref = NotificationPreference(
                user_id=superadmin.id,
                daily_wallpaper=True,
                new_wallpapers=True,
                new_collections=True,
                featured=True,
                promotional=False
            )
            session.add(pref)
            logger.info(f"  + Created initial superadmin: {settings.SUPERADMIN_EMAIL}")

        await session.commit()
        logger.info("==> Development database seed completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_development_data())
