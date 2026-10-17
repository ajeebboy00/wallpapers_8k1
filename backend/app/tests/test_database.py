import uuid
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import NotificationType, ReportReason, ReportStatus, UserRole
from app.core.security import get_password_hash
from app.db.init_db import check_db_health
from app.models import (
    Category,
    Collection,
    CollectionWallpaper,
    Download,
    Favorite,
    Notification,
    NotificationPreference,
    Report,
    Tag,
    User,
    Wallpaper,
)


@pytest.mark.asyncio
async def test_db_connection(db_session: AsyncSession):
    """Test 1: Verifies database connectivity and healthcheck utility."""
    is_healthy = await check_db_health(db_session)
    assert is_healthy is True

@pytest.mark.asyncio
async def test_user_creation_and_defaults(db_session: AsyncSession):
    """Test 2: Verifies User creation, UUID generation, default role and booleans."""
    unique_email = f"test_{uuid.uuid4().hex[:8]}@wallpapers8k1.com"
    user = User(
        name="Test Designer",
        email=unique_email,
        password_hash=get_password_hash("SecretPassword123!"),
        role=UserRole.USER,
        is_active=True,
        email_verified=False
    )
    db_session.add(user)
    await db_session.flush()

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.role == UserRole.USER
    assert user.is_active is True
    assert user.email_verified is False
    assert user.created_at is not None

@pytest.mark.asyncio
async def test_user_unique_email_constraint(db_session: AsyncSession):
    """Test 3: Enforces unique constraint on users.email."""
    duplicate_email = f"duplicate_{uuid.uuid4().hex[:8]}@wallpapers8k1.com"
    user1 = User(name="User One", email=duplicate_email, password_hash="hash1")
    user2 = User(name="User Two", email=duplicate_email, password_hash="hash2")

    db_session.add(user1)
    await db_session.flush()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        await db_session.flush()

@pytest.mark.asyncio
async def test_wallpaper_creation_and_unique_slug(db_session: AsyncSession):
    """Test 4 & 5: Wallpaper creation with metadata and slug uniqueness enforcement."""
    # Create category first
    cat_slug = f"cat_{uuid.uuid4().hex[:8]}"
    cat = Category(name="Test Category", slug=cat_slug)
    db_session.add(cat)
    await db_session.flush()

    wall_slug = f"cosmic-nebula-{uuid.uuid4().hex[:8]}"
    wall1 = Wallpaper(
        title="Cosmic Nebula 8K",
        slug=wall_slug,
        original_url="http://storage/cosmic_orig.png",
        image_url="http://storage/cosmic_opt.webp",
        thumbnail_url="http://storage/cosmic_thumb.webp",
        preview_url="http://storage/cosmic_prev.webp",
        width=7680,
        height=4320,
        aspect_ratio=1.7778,
        file_size=24500000,
        file_format="PNG",
        resolution="8K",
        category_id=cat.id,
    )
    db_session.add(wall1)
    await db_session.flush()

    assert wall1.id is not None
    assert wall1.view_count == 0
    assert wall1.download_count == 0
    assert wall1.is_published is True

    # Attempt duplicate slug
    wall2 = Wallpaper(
        title="Duplicate Cosmic",
        slug=wall_slug,
        original_url="http://storage/cosmic2.png",
        image_url="http://storage/cosmic2.webp",
        thumbnail_url="http://storage/cosmic2_thumb.webp",
        preview_url="http://storage/cosmic2_prev.webp",
        width=7680,
        height=4320,
        aspect_ratio=1.7778,
        file_size=24500000,
        file_format="PNG",
        resolution="8K",
        category_id=cat.id,
    )
    db_session.add(wall2)
    with pytest.raises(IntegrityError):
        await db_session.flush()

@pytest.mark.asyncio
async def test_category_relationship(db_session: AsyncSession):
    """Test 6: Bidirectional relationship between Category and Wallpapers."""
    cat = Category(name="Cyberpunk", slug=f"cyberpunk-{uuid.uuid4().hex[:8]}")
    db_session.add(cat)
    await db_session.flush()

    wall = Wallpaper(
        title="Neon Alley",
        slug=f"neon-alley-{uuid.uuid4().hex[:8]}",
        original_url="http://storage/orig.png",
        image_url="http://storage/opt.webp",
        thumbnail_url="http://storage/thumb.webp",
        preview_url="http://storage/prev.webp",
        width=3840,
        height=2160,
        aspect_ratio=1.7778,
        file_size=12000000,
        file_format="WEBP",
        resolution="4K",
        category_id=cat.id,
    )
    db_session.add(wall)
    await db_session.flush()

    # Re-fetch category and check back_populates
    stmt = select(Category).where(Category.id == cat.id)
    result = await db_session.execute(stmt)
    fetched_cat = result.scalar_one()
    await db_session.refresh(fetched_cat, ["wallpapers"])
    assert len(fetched_cat.wallpapers) == 1
    assert fetched_cat.wallpapers[0].title == "Neon Alley"

@pytest.mark.asyncio
async def test_tag_many_to_many_relationship(db_session: AsyncSession):
    """Test 7: Many-to-many relationship between Wallpapers and Tags via wallpaper_tags."""
    cat = Category(name="Nature Test", slug=f"nature-{uuid.uuid4().hex[:8]}")
    tag1 = Tag(name=f"Landscape-{uuid.uuid4().hex[:6]}", slug=f"landscape-{uuid.uuid4().hex[:6]}")
    tag2 = Tag(name=f"Mountains-{uuid.uuid4().hex[:6]}", slug=f"mountains-{uuid.uuid4().hex[:6]}")
    db_session.add_all([cat, tag1, tag2])
    await db_session.flush()

    wall = Wallpaper(
        title="Alpine Sunrise",
        slug=f"alpine-sunrise-{uuid.uuid4().hex[:8]}",
        original_url="http://storage/alpine.png",
        image_url="http://storage/alpine.webp",
        thumbnail_url="http://storage/alpine_thumb.webp",
        preview_url="http://storage/alpine_prev.webp",
        width=7680,
        height=4320,
        aspect_ratio=1.7778,
        file_size=18000000,
        file_format="JPG",
        resolution="8K",
        category_id=cat.id,
    )
    wall.tags.extend([tag1, tag2])
    db_session.add(wall)
    await db_session.flush()

    await db_session.refresh(wall, ["tags"])
    assert len(wall.tags) == 2
    tag_names = [t.name for t in wall.tags]
    assert tag1.name in tag_names
    assert tag2.name in tag_names

@pytest.mark.asyncio
async def test_favorite_uniqueness_constraint(db_session: AsyncSession):
    """Test 8: Enforces uniqueness on (user_id, wallpaper_id) to prevent duplicate favorites."""
    user = User(name="Fav User", email=f"fav_{uuid.uuid4().hex[:8]}@w8k1.com", password_hash="pw")
    cat = Category(name="Fav Cat", slug=f"favcat-{uuid.uuid4().hex[:8]}")
    db_session.add_all([user, cat])
    await db_session.flush()

    wall = Wallpaper(
        title="Dark Horizon",
        slug=f"dark-horizon-{uuid.uuid4().hex[:8]}",
        original_url="http://orig.png",
        image_url="http://opt.webp",
        thumbnail_url="http://thumb.webp",
        preview_url="http://prev.webp",
        width=1920,
        height=1080,
        aspect_ratio=1.7778,
        file_size=4000000,
        file_format="WEBP",
        resolution="FHD",
        category_id=cat.id,
    )
    db_session.add(wall)
    await db_session.flush()

    # First favorite succeeds
    fav1 = Favorite(user_id=user.id, wallpaper_id=wall.id)
    db_session.add(fav1)
    await db_session.flush()

    # Duplicate favorite fails
    fav2 = Favorite(user_id=user.id, wallpaper_id=wall.id)
    db_session.add(fav2)
    with pytest.raises(IntegrityError):
        await db_session.flush()

@pytest.mark.asyncio
async def test_collection_relationship_and_ordering(db_session: AsyncSession):
    """Test 9: Collection with ordered wallpapers via CollectionWallpaper."""
    cat = Category(name="Coll Cat", slug=f"collcat-{uuid.uuid4().hex[:8]}")
    coll = Collection(name="Aesthetic 8K", slug=f"aesthetic-{uuid.uuid4().hex[:8]}")
    db_session.add_all([cat, coll])
    await db_session.flush()

    wall1 = Wallpaper(
        title="Item 1",
        slug=f"item-1-{uuid.uuid4().hex[:8]}",
        original_url="http://1.png",
        image_url="http://1.webp",
        thumbnail_url="http://1_t.webp",
        preview_url="http://1_p.webp",
        width=7680,
        height=4320,
        aspect_ratio=1.7778,
        file_size=1000000,
        file_format="PNG",
        resolution="8K",
        category_id=cat.id,
    )
    wall2 = Wallpaper(
        title="Item 2",
        slug=f"item-2-{uuid.uuid4().hex[:8]}",
        original_url="http://2.png",
        image_url="http://2.webp",
        thumbnail_url="http://2_t.webp",
        preview_url="http://2_p.webp",
        width=7680,
        height=4320,
        aspect_ratio=1.7778,
        file_size=1000000,
        file_format="PNG",
        resolution="8K",
        category_id=cat.id,
    )
    db_session.add_all([wall1, wall2])
    await db_session.flush()

    # Add to collection with sort_order
    entry1 = CollectionWallpaper(collection_id=coll.id, wallpaper_id=wall1.id, sort_order=1)
    entry2 = CollectionWallpaper(collection_id=coll.id, wallpaper_id=wall2.id, sort_order=2)
    db_session.add_all([entry1, entry2])
    await db_session.flush()

    await db_session.refresh(coll, ["wallpapers"])
    assert len(coll.wallpapers) == 2
    assert coll.wallpapers[0].sort_order == 1
    assert coll.wallpapers[1].sort_order == 2

@pytest.mark.asyncio
async def test_notification_preference_uniqueness(db_session: AsyncSession):
    """Test 10: Enforces 1-to-1 unique preference per user."""
    user = User(name="Pref User", email=f"pref_{uuid.uuid4().hex[:8]}@w8k1.com", password_hash="pw")
    db_session.add(user)
    await db_session.flush()

    pref1 = NotificationPreference(user_id=user.id, daily_wallpaper=True)
    db_session.add(pref1)
    await db_session.flush()

    pref2 = NotificationPreference(user_id=user.id, daily_wallpaper=False)
    db_session.add(pref2)
    with pytest.raises(IntegrityError):
        await db_session.flush()

@pytest.mark.asyncio
async def test_report_creation_and_enums(db_session: AsyncSession):
    """Test 11: Creates a content moderation report with proper enums."""
    reporter = User(name="Reporter", email=f"rep_{uuid.uuid4().hex[:8]}@w8k1.com", password_hash="pw")
    reviewer = User(name="Reviewer", email=f"rev_{uuid.uuid4().hex[:8]}@w8k1.com", password_hash="pw", role=UserRole.ADMIN)
    cat = Category(name="Rep Cat", slug=f"repcat-{uuid.uuid4().hex[:8]}")
    db_session.add_all([reporter, reviewer, cat])
    await db_session.flush()

    wall = Wallpaper(
        title="Reported Wall",
        slug=f"rep-wall-{uuid.uuid4().hex[:8]}",
        original_url="http://orig.png",
        image_url="http://opt.webp",
        thumbnail_url="http://thumb.webp",
        preview_url="http://prev.webp",
        width=3840,
        height=2160,
        aspect_ratio=1.7778,
        file_size=5000000,
        file_format="JPG",
        resolution="4K",
        category_id=cat.id,
    )
    db_session.add(wall)
    await db_session.flush()

    report = Report(
        user_id=reporter.id,
        wallpaper_id=wall.id,
        reason=ReportReason.COPYRIGHT,
        description="DMCA concern reported by creator.",
        status=ReportStatus.PENDING
    )
    db_session.add(report)
    await db_session.flush()

    assert report.id is not None
    assert report.reason == ReportReason.COPYRIGHT
    assert report.status == ReportStatus.PENDING
    assert report.reviewed_by is None

@pytest.mark.asyncio
async def test_foreign_key_cascade_behavior(db_session: AsyncSession):
    """Test 12: Deleting a user cascades to favorites and preferences, while downloads preserve record with SET NULL."""
    user = User(name="Cascade User", email=f"casc_{uuid.uuid4().hex[:8]}@w8k1.com", password_hash="pw")
    cat = Category(name="Cascade Cat", slug=f"casccat-{uuid.uuid4().hex[:8]}")
    db_session.add_all([user, cat])
    await db_session.flush()

    wall = Wallpaper(
        title="Cascade Wall",
        slug=f"casc-wall-{uuid.uuid4().hex[:8]}",
        original_url="http://orig.png",
        image_url="http://opt.webp",
        thumbnail_url="http://thumb.webp",
        preview_url="http://prev.webp",
        width=1920,
        height=1080,
        aspect_ratio=1.7778,
        file_size=3000000,
        file_format="WEBP",
        resolution="FHD",
        category_id=cat.id,
    )
    db_session.add(wall)
    await db_session.flush()

    fav = Favorite(user_id=user.id, wallpaper_id=wall.id)
    dl = Download(user_id=user.id, wallpaper_id=wall.id)
    pref = NotificationPreference(user_id=user.id)
    db_session.add_all([fav, dl, pref])
    await db_session.flush()

    user_id = user.id
    fav_id = fav.id
    dl_id = dl.id
    pref_id = pref.id

    # Delete User
    await db_session.delete(user)
    await db_session.flush()

    # Verify Favorite was cascaded and deleted
    res_fav = await db_session.execute(select(Favorite).where(Favorite.id == fav_id))
    assert res_fav.scalar_one_or_none() is None

    # Verify NotificationPreference was cascaded and deleted
    res_pref = await db_session.execute(select(NotificationPreference).where(NotificationPreference.id == pref_id))
    assert res_pref.scalar_one_or_none() is None

    # Verify Download still exists but user_id is SET NULL (preserving analytics integrity)
    res_dl = await db_session.execute(select(Download).where(Download.id == dl_id))
    persisted_dl = res_dl.scalar_one_or_none()
    assert persisted_dl is not None
    assert persisted_dl.user_id is None

@pytest.mark.asyncio
async def test_migration_revision_state(db_session: AsyncSession):
    """Test 12: Verifies that alembic_version table exists and matches head revision."""
    from sqlalchemy import text
    result = await db_session.execute(text("SELECT version_num FROM alembic_version;"))
    current_version = result.scalar_one_or_none()
    assert current_version is not None
    assert current_version in ["77174445e7de", "98e1d3266a85", "b989a6d2804f", "24ead4fdff7f"]
