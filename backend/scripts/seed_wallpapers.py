"""
WALLPAPERS_8K1 — DEVELOPMENT TEST WALLPAPER SEEDER
Imports 30 genuine, downloadable, legally licensed test wallpaper images from Unsplash
under the Unsplash License (free commercial & non-commercial use with attribution).

Guards:
- Refuses to execute in production (APP_ENV=production or production DB URL).
- Idempotent: Skips wallpapers if already imported (stable slug matching).
- Validates every image through Pillow pipeline (magic bytes & dimensions).
- Generates 4 tiers: Original, Optimized (WebP), Preview (WebP), Thumbnail (WebP).
- Never deletes existing data or production data.
"""

import asyncio
import os
import sys
import time
import urllib.request
import uuid
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.config import settings
from app.core.logging import logger
from app.core.utils import generate_slug
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.models.category import Category
from app.models.tag import Tag
from app.models.user import User
from app.models.wallpaper import Wallpaper
from app.repositories.tag_repository import TagRepository
from app.services.ai_vision_service import AIVisionService
from app.storage import get_storage_provider
from app.storage.image_processor import ImageProcessor

# -----------------------------------------------------------------------------
# 30 Curated Legally Usable Test Wallpapers across 8 Required Categories
# License: Unsplash License (https://unsplash.com/license)
# -----------------------------------------------------------------------------
TEST_WALLPAPERS_CATALOG = [
    # 1. Nature (4)
    {
        "title": "Yosemite Mirror Lake",
        "category_slug": "nature",
        "category_name": "Nature",
        "author": "Bailey Zindel",
        "license": "Unsplash License",
        "description": "Crystal clear water reflection of sheer granite cliffs under dawn light in Yosemite Valley.",
        "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=2560&q=85",
        "tags": ["nature", "mountains", "yosemite", "lake", "reflection", "scenic"],
        "is_featured": True,
        "is_trending": True,
        "is_daily": True,
    },
    {
        "title": "Foggy Alpine Valley",
        "category_slug": "nature",
        "category_name": "Nature",
        "author": "Jerry Zhang",
        "license": "Unsplash License",
        "description": "Dramatic mountain peaks blanketed by morning mist and ancient evergreen pine forest.",
        "url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=2560&q=85",
        "tags": ["nature", "alpine", "fog", "pine", "wilderness", "foggy"],
        "is_featured": True,
        "is_trending": False,
        "is_daily": False,
    },
    {
        "title": "Emerald River Canyon",
        "category_slug": "nature",
        "category_name": "Nature",
        "author": "Kalen Emsley",
        "license": "Unsplash License",
        "description": "Vibrant emerald green glacial river winding through dramatic rugged canyon terrain.",
        "url": "https://images.unsplash.com/photo-1426604966848-d7adac402bff?auto=format&fit=crop&w=2560&q=85",
        "tags": ["nature", "river", "canyon", "emerald", "valley", "green"],
        "is_featured": False,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Golden Meadow Horizon",
        "category_slug": "nature",
        "category_name": "Nature",
        "author": "Sébastien Jermer",
        "license": "Unsplash License",
        "description": "Rolling hills of golden grass illuminated by warm afternoon sun beneath blue skies.",
        "url": "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?auto=format&fit=crop&w=2560&q=85",
        "tags": ["nature", "meadow", "hills", "golden-hour", "horizon", "peaceful"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },

    # 2. AMOLED / Black (4)
    {
        "title": "Dark Poly Geo",
        "category_slug": "amoled-black",
        "category_name": "AMOLED / Black",
        "author": "Steve Johnson",
        "license": "Unsplash License",
        "description": "Pure black 3D geometric relief polygons with subtle dark highlights for OLED battery saving.",
        "url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=2560&q=85",
        "tags": ["amoled", "black", "dark", "polygons", "geometry", "minimalist"],
        "is_featured": True,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Obsidian Liquid Flow",
        "category_slug": "amoled-black",
        "category_name": "AMOLED / Black",
        "author": "Fakurian Design",
        "license": "Unsplash License",
        "description": "High contrast liquid chrome ribbons glistening over true black pitch void.",
        "url": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=2560&q=85",
        "tags": ["amoled", "black", "liquid", "chrome", "obsidian", "dark-mode"],
        "is_featured": True,
        "is_trending": False,
        "is_daily": False,
    },
    {
        "title": "Midnight Neon Rain",
        "category_slug": "amoled-black",
        "category_name": "AMOLED / Black",
        "author": "Aleksandar Pasaric",
        "license": "Unsplash License",
        "description": "Futuristic neon city boulevard reflections against deep dark night pavement.",
        "url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=2560&q=85",
        "tags": ["amoled", "neon", "tokyo", "rain", "cyberpunk", "dark"],
        "is_featured": False,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Dark Minimalist Waves",
        "category_slug": "amoled-black",
        "category_name": "AMOLED / Black",
        "author": "Milad Fakurian",
        "license": "Unsplash License",
        "description": "Smooth dark matte satin waves folding gracefully into infinite black space.",
        "url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=2560&q=85",
        "tags": ["amoled", "minimal", "waves", "satin", "black", "deep-black"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },

    # 3. Abstract (4)
    {
        "title": "Liquid Prism Swirl",
        "category_slug": "abstract",
        "category_name": "Abstract",
        "author": "Philip Oroni",
        "license": "Unsplash License",
        "description": "Iridescent fluid spectrum ribbons twisting through space with glass refraction.",
        "url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=2560&q=85",
        "tags": ["abstract", "prism", "iridescent", "3d", "refraction", "colors"],
        "is_featured": True,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Gradient Sphere Waves",
        "category_slug": "abstract",
        "category_name": "Abstract",
        "author": "Milad Fakurian",
        "license": "Unsplash License",
        "description": "Soft pastel floating 3D spheres surrounded by flowing digital cloth textures.",
        "url": "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?auto=format&fit=crop&w=2560&q=85",
        "tags": ["abstract", "gradient", "spheres", "pastel", "render", "fluid"],
        "is_featured": False,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Vibrant Chroma Splash",
        "category_slug": "abstract",
        "category_name": "Abstract",
        "author": "Lucas Benjamin",
        "license": "Unsplash License",
        "description": "High-speed explosion of vibrant neon ink pigments in crystal water suspension.",
        "url": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=2560&q=85",
        "tags": ["abstract", "chroma", "paint", "splash", "vibrant", "colorful"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },
    {
        "title": "Surreal Acrylic Cloud",
        "category_slug": "abstract",
        "category_name": "Abstract",
        "author": "Pawel Czerwinski",
        "license": "Unsplash License",
        "description": "Surreal marbling texture with intricate gold and turquoise mineral veining.",
        "url": "https://images.unsplash.com/photo-1574169208507-84376144848b?auto=format&fit=crop&w=2560&q=85",
        "tags": ["abstract", "acrylic", "marble", "mineral", "turquoise", "textures"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },

    # 4. Cars (4)
    {
        "title": "Porsche Carrera GT3",
        "category_slug": "cars",
        "category_name": "Cars",
        "author": "Campbell",
        "license": "Unsplash License",
        "description": "Aerodynamic high-downforce Porsche 911 GT3 rear profile on empty asphalt.",
        "url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=2560&q=85",
        "tags": ["cars", "porsche", "supercar", "motorsport", "gt3", "speed"],
        "is_featured": True,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Crimson Apex Supercar",
        "category_slug": "cars",
        "category_name": "Cars",
        "author": "Chuttersnap",
        "license": "Unsplash License",
        "description": "Lethal crimson exotic sports car cornering at high velocity on mountain pass.",
        "url": "https://images.unsplash.com/photo-1525609004556-c46c7d6cf023?auto=format&fit=crop&w=2560&q=85",
        "tags": ["cars", "supercar", "red", "exotic", "velocity", "racing"],
        "is_featured": False,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Midnight Speedster",
        "category_slug": "cars",
        "category_name": "Cars",
        "author": "Dhiva Krishna",
        "license": "Unsplash License",
        "description": "Sleek matte coupe lights cutting through nighttime atmospheric fog.",
        "url": "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=2560&q=85",
        "tags": ["cars", "coupe", "night", "headlights", "automotive", "speedster"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },
    {
        "title": "Cyber Track Machine",
        "category_slug": "cars",
        "category_name": "Cars",
        "author": "Stefan Rodriguez",
        "license": "Unsplash License",
        "description": "High performance mid-engine supercar parked under cool warehouse industrial lights.",
        "url": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=2560&q=85",
        "tags": ["cars", "corvette", "supercar", "performance", "track", "metallic"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },

    # 5. Flowers (4)
    {
        "title": "Sakura Blossom Spring",
        "category_slug": "flowers",
        "category_name": "Flowers",
        "author": "Chuttersnap",
        "license": "Unsplash License",
        "description": "Delicate pastel pink cherry blossoms in full Japanese spring bloom against sky.",
        "url": "https://images.unsplash.com/photo-1508610048659-a06b669e3321?auto=format&fit=crop&w=2560&q=85",
        "tags": ["flowers", "sakura", "cherry-blossom", "spring", "pink", "floral"],
        "is_featured": True,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "White Peony Petals",
        "category_slug": "flowers",
        "category_name": "Flowers",
        "author": "Scott Webb",
        "license": "Unsplash License",
        "description": "High magnification macro view of pristine white peony petals with dew droplets.",
        "url": "https://images.unsplash.com/photo-1526047932273-341f2a7631f9?auto=format&fit=crop&w=2560&q=85",
        "tags": ["flowers", "peony", "macro", "white", "botanical", "delicate"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },
    {
        "title": "Sunlit Meadow Bloom",
        "category_slug": "flowers",
        "category_name": "Flowers",
        "author": "Aaron Burden",
        "license": "Unsplash License",
        "description": "Golden hour sun flare warming wild field flowers with shallow depth of field.",
        "url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=2560&q=85",
        "tags": ["flowers", "sunflower", "sunlight", "golden", "meadow", "summer"],
        "is_featured": False,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Velvet Rose Close Up",
        "category_slug": "flowers",
        "category_name": "Flowers",
        "author": "Luca Baggio",
        "license": "Unsplash License",
        "description": "Intense crimson velvet rose petal spiral detail captured with clinical clarity.",
        "url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=2560&q=85",
        "tags": ["flowers", "rose", "red", "velvet", "romantic", "macro"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },

    # 6. Minimal (4)
    {
        "title": "Clean Dune Shadow",
        "category_slug": "minimal",
        "category_name": "Minimal",
        "author": "Sean Oulashin",
        "license": "Unsplash License",
        "description": "Razor sharp knife-edge ridge of pristine sand dune dividing light and shadow.",
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=2560&q=85",
        "tags": ["minimal", "dune", "desert", "sand", "shadow", "clean"],
        "is_featured": True,
        "is_trending": False,
        "is_daily": False,
    },
    {
        "title": "Concrete Geometry Wall",
        "category_slug": "minimal",
        "category_name": "Minimal",
        "author": "Jilbert Ebrahimi",
        "license": "Unsplash License",
        "description": "Minimalist architectural concrete surface with crisp diagonal sunlight cast shadow.",
        "url": "https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=2560&q=85",
        "tags": ["minimal", "concrete", "geometry", "shadow", "lines", "brutalist"],
        "is_featured": False,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Misty Lake Stillness",
        "category_slug": "minimal",
        "category_name": "Minimal",
        "author": "Luca Bravo",
        "license": "Unsplash License",
        "description": "Completely glass-calm alpine lake vanishing into monochrome grey morning fog.",
        "url": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=2560&q=85",
        "tags": ["minimal", "lake", "mist", "stillness", "calm", "zen"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },
    {
        "title": "Pastel Dusk Horizon",
        "category_slug": "minimal",
        "category_name": "Minimal",
        "author": "Paul Pastourmatzis",
        "license": "Unsplash License",
        "description": "Subtle ombre sky transitioning gently from pale peach to twilight periwinkle.",
        "url": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=2560&q=85",
        "tags": ["minimal", "dusk", "horizon", "pastel", "sky", "gradient"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },

    # 7. Space (3)
    {
        "title": "Cosmic Stardust Nebula",
        "category_slug": "space",
        "category_name": "Space",
        "author": "Jeremy Thomas",
        "license": "Unsplash License",
        "description": "Dense starfield explosion illuminating interstellar purple and cyan gas clouds.",
        "url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=2560&q=85",
        "tags": ["space", "nebula", "cosmos", "stars", "galaxy", "astronomy"],
        "is_featured": True,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Orbit Earth Night",
        "category_slug": "space",
        "category_name": "Space",
        "author": "NASA",
        "license": "Public Domain / Unsplash",
        "description": "Atmospheric curvature of Earth from orbit with glowing city networks and stars.",
        "url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=2560&q=85",
        "tags": ["space", "earth", "orbit", "nasa", "planet", "night-lights"],
        "is_featured": True,
        "is_trending": False,
        "is_daily": False,
    },
    {
        "title": "Infinite Galaxy Core",
        "category_slug": "space",
        "category_name": "Space",
        "author": "Ryan Hutton",
        "license": "Unsplash License",
        "description": "Milky Way spiral galactic arm arching over a silhouetted wilderness horizon.",
        "url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=2560&q=85",
        "tags": ["space", "milkyway", "galaxy", "astrophotography", "stars", "night-sky"],
        "is_featured": False,
        "is_trending": True,
        "is_daily": False,
    },

    # 8. Architecture (3)
    {
        "title": "Spiral Monolith Stairs",
        "category_slug": "architecture",
        "category_name": "Architecture",
        "author": "Dan Freeman",
        "license": "Unsplash License",
        "description": "Hypnotic geometric spiral staircase descending in rhythmic architectural curves.",
        "url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=2560&q=85",
        "tags": ["architecture", "spiral", "staircase", "geometry", "modern", "structural"],
        "is_featured": True,
        "is_trending": True,
        "is_daily": False,
    },
    {
        "title": "Modern Glass Skyline",
        "category_slug": "architecture",
        "category_name": "Architecture",
        "author": "Sean Pollock",
        "license": "Unsplash License",
        "description": "Towering vertical perspective looking up between mirrored glass skyscrapers.",
        "url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=2560&q=85",
        "tags": ["architecture", "skyscraper", "skyline", "glass", "urban", "modern"],
        "is_featured": False,
        "is_trending": False,
        "is_daily": False,
    },
    {
        "title": "Curved White Facade",
        "category_slug": "architecture",
        "category_name": "Architecture",
        "author": "Victor Garcia",
        "license": "Unsplash License",
        "description": "Futuristic flowing parametric white building exterior with clean sunlight shadows.",
        "url": "https://images.unsplash.com/photo-1511818966892-d7d671e672a2?auto=format&fit=crop&w=2560&q=85",
        "tags": ["architecture", "parametric", "facade", "minimalist", "white", "curves"],
        "is_featured": False,
        "is_trending": True,
        "is_daily": False,
    },
]

# -----------------------------------------------------------------------------
# Seeder Implementation
# -----------------------------------------------------------------------------
async def seed_wallpapers():
    print("=" * 70)
    print("WALLPAPERS_8K1 — AUTOMATIC TEST WALLPAPER SEEDER")
    print("=" * 70)

    # 1. SAFETY CHECKS (Requirement 8)
    if settings.APP_ENV == "production":
        print("[ERROR] SAFETY GUARD TRIGGERED: Cannot run seed command in production (APP_ENV=production).")
        sys.exit(1)

    db_url_lower = settings.DATABASE_URL.lower()
    if "prod" in db_url_lower or "production" in db_url_lower:
        print("[ERROR] SAFETY GUARD TRIGGERED: Database URL matches production pattern! Aborting.")
        sys.exit(1)

    print(f"[*] Environment: {settings.APP_ENV}")
    print(f"[*] Database target: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")
    print(f"[*] Storage provider: {settings.STORAGE_PROVIDER}")
    print(f"[*] Target seed items: {len(TEST_WALLPAPERS_CATALOG)}")
    print("-" * 70)

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    storage = get_storage_provider()

    # Track metrics
    imported_count = 0
    skipped_count = 0
    failed_count = 0

    async with AsyncSessionLocal() as session:
        tag_repo = TagRepository(session)

        # Retrieve superadmin user as uploader
        stmt = select(User).where(User.email == settings.SUPERADMIN_EMAIL)
        admin_user = (await session.execute(stmt)).scalar_one_or_none()
        uploader_id = admin_user.id if admin_user else None

        # Pre-resolve categories
        cat_cache: Dict[str, Category] = {}

        for idx, item in enumerate(TEST_WALLPAPERS_CATALOG, 1):
            title = item["title"]
            cat_slug = item["category_slug"]
            cat_name = item["category_name"]
            image_url = item["url"]
            expected_slug = generate_slug(title, fallback_prefix="wallpaper")

            print(f"[{idx:02d}/30] Processing: \"{title}\" ({cat_name})...", end=" ", flush=True)

            # Check idempotency: does wallpaper with this slug already exist? (Requirement 5)
            check_stmt = select(Wallpaper).where(Wallpaper.slug == expected_slug)
            existing_wp = (await session.execute(check_stmt)).scalar_one_or_none()
            if existing_wp:
                print(f"[SKIPPED] (Already exists in database: id={existing_wp.id})")
                skipped_count += 1
                continue

            # Ensure category exists
            if cat_slug not in cat_cache:
                stmt_c = select(Category).where(Category.slug == cat_slug)
                cat = (await session.execute(stmt_c)).scalar_one_or_none()
                if not cat:
                    cat = Category(
                        name=cat_name,
                        slug=cat_slug,
                        description=f"Curated 8K {cat_name} collection",
                        is_active=True
                    )
                    session.add(cat)
                    await session.flush()
                cat_cache[cat_slug] = cat

            category = cat_cache[cat_slug]

            # 2. Download actual image file (Requirement 3)
            try:
                req = urllib.request.Request(
                    image_url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Wallpapers8k1-Seeder/1.0"}
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"HTTP {resp.status} download failed")
                    file_bytes = resp.read()
            except Exception as dl_err:
                print(f"[FAILED] Download error: {dl_err}")
                failed_count += 1
                continue

            # 3. Validate image and generate multi-tier variants (Requirement 3)
            try:
                filename = f"{expected_slug}.jpg"
                processed = ImageProcessor.process_image(file_bytes, filename=filename)
            except Exception as proc_err:
                print(f"[FAILED] Image validation/processing error: {proc_err}")
                failed_count += 1
                continue

            # 4. Persist variants to local storage (Requirement 3 & 4)
            try:
                unique_file_id = uuid.uuid4().hex[:12]
                base_storage_path = f"wallpapers/{cat_slug}/{expected_slug}_{unique_file_id}"

                orig_path = f"{base_storage_path}_original{processed.original_extension}"
                opt_path = f"{base_storage_path}_optimized.webp"
                prev_path = f"{base_storage_path}_preview.webp"
                thumb_path = f"{base_storage_path}_thumbnail.webp"

                stored_orig_url = await storage.save(processed.original_bytes, orig_path, f"image/{processed.file_format}")
                stored_img_url = await storage.save(processed.optimized_bytes, opt_path, "image/webp")
                stored_prev_url = await storage.save(processed.preview_bytes, prev_path, "image/webp")
                stored_thumb_url = await storage.save(processed.thumbnail_bytes, thumb_path, "image/webp")
            except Exception as store_err:
                print(f"[FAILED] Storage save error: {store_err}")
                failed_count += 1
                continue

            # 5. Extract AI Vision attributes & color metadata
            ai_meta = AIVisionService.analyze_and_extract_metadata(
                title=title,
                category_name=cat_name,
                description=item["description"],
                existing_tags=item["tags"]
            )

            # 6. Resolve Tags
            tag_objs = []
            if item.get("tags"):
                tag_objs = await tag_repo.get_or_create_batch(item["tags"])

            # 7. Create Database Record (Requirement 3 & 4)
            # Set is_published=True ONLY after files & metadata are safely stored
            full_description = (
                f"{item['description']}\n\n"
                f"Photo by {item['author']} on Unsplash.\n"
                f"License: {item['license']} (https://unsplash.com/license)."
            )

            wallpaper = Wallpaper(
                title=title,
                slug=expected_slug,
                description=full_description,
                original_url=stored_orig_url,
                image_url=stored_img_url,
                thumbnail_url=stored_thumb_url,
                preview_url=stored_prev_url,
                width=processed.width,
                height=processed.height,
                aspect_ratio=processed.aspect_ratio,
                file_size=processed.file_size,
                file_format=processed.file_format,
                resolution=processed.resolution,
                category_id=category.id,
                uploader_id=uploader_id,
                is_featured=item.get("is_featured", False),
                is_trending=item.get("is_trending", False),
                is_daily=item.get("is_daily", False),
                is_published=True,  # Published only after storage persistence
                is_premium=False,
                view_count=100 + (idx * 37) % 500,
                download_count=30 + (idx * 19) % 250,
                favorite_count=15 + (idx * 11) % 120,
                dominant_color=ai_meta.get("dominant_color"),
                color_palette=ai_meta.get("color_palette"),
                perceptual_hash=ai_meta.get("perceptual_hash"),
                ai_tags=ai_meta.get("ai_tags"),
                tags=tag_objs
            )

            session.add(wallpaper)
            await session.commit()

            print(f"[SUCCESS] Saved {processed.width}x{processed.height} ({processed.resolution}) -> thumb: {len(processed.thumbnail_bytes):,}B")
            imported_count += 1

    print("-" * 70)
    print("SEEDING SUMMARY REPORT:")
    print(f"  • Total Catalog Target : {len(TEST_WALLPAPERS_CATALOG)}")
    print(f"  • Successfully Imported: {imported_count}")
    print(f"  • Skipped (Idempotent) : {skipped_count}")
    print(f"  • Failed Downloads     : {failed_count}")

    # Final DB count check
    async with AsyncSessionLocal() as session:
        count_stmt = select(Wallpaper)
        all_wps = (await session.execute(count_stmt)).scalars().all()
        print(f"  • Total DB Wallpapers  : {len(all_wps)}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(seed_wallpapers())
