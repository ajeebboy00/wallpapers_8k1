import uuid
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import generate_slug
from app.models.tag import Tag, wallpaper_tags
from app.repositories.base import BaseRepository

class TagRepository(BaseRepository[Tag]):
    def __init__(self, session: AsyncSession):
        super().__init__(Tag, session)

    async def get_by_slug(self, slug: str) -> Optional[Tag]:
        stmt = select(Tag).where(Tag.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Tag]:
        stmt = select(Tag).where(func.lower(Tag.name) == name.strip().lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_batch(self, tag_names: List[str]) -> List[Tag]:
        """Ensures all requested tags exist, returning their Tag models."""
        cleaned_names = list({name.strip() for name in tag_names if name.strip()})
        if not cleaned_names:
            return []

        lower_to_original = {name.lower(): name for name in cleaned_names}

        # Query existing tags
        stmt = select(Tag).where(func.lower(Tag.name).in_(lower_to_original.keys()))
        result = await self.session.execute(stmt)
        existing_tags = list(result.scalars().all())
        existing_names_lower = {tag.name.lower() for tag in existing_tags}

        # Create missing tags
        created_tags: List[Tag] = []
        for lower_name, original_name in lower_to_original.items():
            if lower_name not in existing_names_lower:
                base_slug = generate_slug(original_name, fallback_prefix="tag")
                # Ensure unique slug
                slug = base_slug
                counter = 1
                while True:
                    check_stmt = select(Tag).where(Tag.slug == slug)
                    if not (await self.session.execute(check_stmt)).scalar_one_or_none():
                        break
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                new_tag = Tag(name=original_name, slug=slug)
                self.session.add(new_tag)
                created_tags.append(new_tag)

        if created_tags:
            await self.session.flush()

        return existing_tags + created_tags

    async def get_popular_tags(self, limit: int = 30) -> List[Tag]:
        """Fetch tags ordered by wallpaper association count."""
        stmt = (
            select(Tag)
            .join(wallpaper_tags, wallpaper_tags.c.tag_id == Tag.id)
            .group_by(Tag.id)
            .order_by(func.count(wallpaper_tags.c.wallpaper_id).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
