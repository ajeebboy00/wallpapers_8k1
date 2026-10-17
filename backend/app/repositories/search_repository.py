import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import case, distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.tag import Tag, wallpaper_tags
from app.models.wallpaper import Wallpaper
from app.schemas.search import (
    ColorStat,
    SearchAnalyticsResponse,
    SearchFilterParams,
    SearchSuggestionsResponse,
    SimilarWallpaperItem,
)
from app.services.ai_vision_service import AIVisionService, COLOR_PRESETS

class SearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_wallpapers(
        self,
        params: SearchFilterParams,
        offset: int = 0,
        limit: int = 20
    ) -> Tuple[List[Wallpaper], int]:
        """Searches wallpapers across title, description, AI tags, category, and dominant color with fuzzy trigram matching."""
        query = select(Wallpaper).where(Wallpaper.is_published.is_(True))

        q_clean = params.q.strip() if params.q else None

        # 1. Advanced Full-Text & Trigram Fuzzy Matching
        if q_clean:
            q_pattern = f"%{q_clean}%"

            # Subquery matching tag names or slugs
            tag_subq = (
                select(wallpaper_tags.c.wallpaper_id)
                .join(Tag, Tag.id == wallpaper_tags.c.tag_id)
                .where(
                    or_(
                        Tag.name.ilike(q_pattern),
                        Tag.slug.ilike(q_pattern),
                        func.similarity(Tag.name, q_clean) > 0.3
                    )
                )
            )

            # Subquery matching category names or slugs
            cat_subq = (
                select(Category.id)
                .where(
                    or_(
                        Category.name.ilike(q_pattern),
                        Category.slug.ilike(q_pattern),
                        func.similarity(Category.name, q_clean) > 0.3
                    )
                )
            )

            text_condition = or_(
                Wallpaper.title.ilike(q_pattern),
                Wallpaper.description.ilike(q_pattern),
                Wallpaper.ai_description.ilike(q_pattern),
                func.similarity(Wallpaper.title, q_clean) > 0.2,
                func.similarity(func.coalesce(Wallpaper.description, ""), q_clean) > 0.2,
                Wallpaper.id.in_(tag_subq),
                Wallpaper.category_id.in_(cat_subq)
            )
            query = query.where(text_condition)

        # 2. Category Filter (slug or UUID)
        if params.category:
            try:
                cat_uuid = uuid.UUID(params.category)
                query = query.where(Wallpaper.category_id == cat_uuid)
            except ValueError:
                cat_slug_subq = select(Category.id).where(Category.slug == params.category)
                query = query.where(Wallpaper.category_id.in_(cat_slug_subq))

        # 3. Tag Filter (slug or name)
        if params.tag:
            tag_filter_subq = (
                select(wallpaper_tags.c.wallpaper_id)
                .join(Tag, Tag.id == wallpaper_tags.c.tag_id)
                .where(
                    or_(
                        Tag.slug == params.tag,
                        Tag.name.ilike(params.tag)
                    )
                )
            )
            query = query.where(Wallpaper.id.in_(tag_filter_subq))

        # 4. Color Palette & Dominant Color Filter
        if params.color:
            target_rgb = AIVisionService.parse_hex_color(params.color)
            if target_rgb:
                hex_normalized = AIVisionService.rgb_to_hex(*target_rgb)
                # Match dominant color or presence in color palette
                color_condition = or_(
                    Wallpaper.dominant_color.ilike(f"%{hex_normalized[1:]}%"),
                    Wallpaper.dominant_color == hex_normalized,
                    func.cast(Wallpaper.color_palette, func.text).ilike(f"%{hex_normalized}%")
                )
                query = query.where(color_condition)

        # 5. Resolution Filter
        if params.resolution:
            query = query.where(Wallpaper.resolution == params.resolution)

        # 6. Orientation Filter
        if params.orientation == "portrait":
            query = query.where(Wallpaper.height > Wallpaper.width)
        elif params.orientation == "landscape":
            query = query.where(Wallpaper.width > Wallpaper.height)
        elif params.orientation == "square":
            query = query.where(Wallpaper.width == Wallpaper.height)

        # 7. Premium Filter
        if params.is_premium is not None:
            query = query.where(Wallpaper.is_premium == params.is_premium)

        # 8. AI Generated Filter
        if params.is_ai_generated is not None:
            query = query.where(Wallpaper.is_ai_generated == params.is_ai_generated)

        # 9. Count total matching rows
        count_subq = query.subquery()
        count_stmt = select(func.count(distinct(count_subq.c.id))).select_from(count_subq)
        total_count = (await self.session.execute(count_stmt)).scalar() or 0

        # 10. Dynamic Sorting & Trigram Relevance Ranking
        if params.sort == "relevance" and q_clean:
            q_lower = q_clean.lower()
            relevance_rank = case(
                (func.lower(Wallpaper.title) == q_lower, 100),
                (func.lower(Wallpaper.title).startswith(q_lower), 75),
                (func.lower(Wallpaper.title).contains(q_lower), 50),
                (func.similarity(Wallpaper.title, q_clean) > 0.4, 40),
                (func.lower(Wallpaper.description).contains(q_lower), 25),
                else_=10
            )
            if params.order == "asc":
                query = query.order_by(
                    relevance_rank.asc(),
                    Wallpaper.trending_score.asc(),
                    Wallpaper.created_at.asc(),
                    Wallpaper.id.asc()
                )
            else:
                query = query.order_by(
                    relevance_rank.desc(),
                    Wallpaper.trending_score.desc(),
                    Wallpaper.created_at.desc(),
                    Wallpaper.id.desc()
                )
        else:
            order_col = Wallpaper.created_at
            if params.sort in ("popular", "downloads"):
                order_col = Wallpaper.download_count
            elif params.sort == "views":
                order_col = Wallpaper.view_count
            elif params.sort == "favorites":
                order_col = Wallpaper.favorite_count
            elif params.sort == "trending":
                order_col = Wallpaper.trending_score
            elif params.sort == "oldest":
                order_col = Wallpaper.created_at

            if params.order == "asc":
                query = query.order_by(order_col.asc(), Wallpaper.id.asc())
            else:
                query = query.order_by(order_col.desc(), Wallpaper.id.desc())

        # 11. Pagination & Eager Loading
        paginated_query = (
            query
            .offset(offset)
            .limit(limit)
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
        )

        result = await self.session.execute(paginated_query)
        items = list(result.scalars().all())
        return items, total_count

    async def get_similar_wallpapers(
        self,
        wallpaper_id: uuid.UUID,
        limit: int = 10,
    ) -> List[Tuple[Wallpaper, float, List[str]]]:
        """Calculates multi-dimensional visual and semantic similarity for a wallpaper."""
        # Fetch target wallpaper
        stmt = (
            select(Wallpaper)
            .where(Wallpaper.id == wallpaper_id)
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
        )
        res = await self.session.execute(stmt)
        source = res.scalars().first()
        if not source:
            return []

        # Prepare source dictionary
        source_dict = {
            "title": source.title,
            "category_id": source.category_id,
            "dominant_color": source.dominant_color,
            "perceptual_hash": source.perceptual_hash,
            "resolution": source.resolution,
            "tags": [t.name for t in source.tags],
            "ai_tags": source.ai_tags or [],
        }

        # Fetch candidate wallpapers
        cand_stmt = (
            select(Wallpaper)
            .where(
                Wallpaper.id != wallpaper_id,
                Wallpaper.is_published.is_(True)
            )
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
            .limit(50)
        )
        cand_res = await self.session.execute(cand_stmt)
        candidates = cand_res.scalars().all()

        scored_candidates: List[Tuple[Wallpaper, float, List[str]]] = []
        for cand in candidates:
            cand_dict = {
                "title": cand.title,
                "category_id": cand.category_id,
                "dominant_color": cand.dominant_color,
                "perceptual_hash": cand.perceptual_hash,
                "resolution": cand.resolution,
                "tags": [t.name for t in cand.tags],
                "ai_tags": cand.ai_tags or [],
            }
            score, factors = AIVisionService.calculate_similarity_score(source_dict, cand_dict)
            scored_candidates.append((cand, score, factors))

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[:limit]

    async def batch_process_ai_tagging(
        self,
        limit: int = 50,
        force_reprocess: bool = False,
        wallpaper_id: Optional[uuid.UUID] = None,
    ) -> List[Wallpaper]:
        """Runs automated AI vision tagging & color extraction on target wallpapers."""
        stmt = (
            select(Wallpaper)
            .options(
                selectinload(Wallpaper.category),
                selectinload(Wallpaper.tags)
            )
        )
        if wallpaper_id:
            stmt = stmt.where(Wallpaper.id == wallpaper_id)
        elif not force_reprocess:
            stmt = stmt.where(
                or_(
                    Wallpaper.dominant_color.is_(None),
                    Wallpaper.ai_tags.is_(None),
                    Wallpaper.perceptual_hash.is_(None),
                )
            )

        stmt = stmt.limit(limit)
        res = await self.session.execute(stmt)
        wallpapers = res.scalars().all()

        updated: List[Wallpaper] = []
        for wp in wallpapers:
            category_name = wp.category.name if wp.category else None
            existing_tags = [t.name for t in wp.tags]

            ai_meta = AIVisionService.analyze_and_extract_metadata(
                title=wp.title,
                category_name=category_name,
                description=wp.description,
                existing_tags=existing_tags,
            )

            wp.dominant_color = ai_meta["dominant_color"]
            wp.color_palette = ai_meta["color_palette"]
            wp.perceptual_hash = ai_meta["perceptual_hash"]
            wp.ai_tags = ai_meta["ai_tags"]
            wp.ai_description = ai_meta["ai_description"]
            wp.is_ai_generated = ai_meta["is_ai_generated"]

            updated.append(wp)

        if updated:
            await self.session.commit()
            for wp in updated:
                await self.session.refresh(wp)

        return updated

    async def get_search_analytics(self) -> SearchAnalyticsResponse:
        """Returns search and color distribution analytics for the admin panel."""
        total_stmt = select(func.count(Wallpaper.id))
        total_count = (await self.session.execute(total_stmt)).scalar() or 0

        ai_indexed_stmt = select(func.count(Wallpaper.id)).where(Wallpaper.dominant_color.isnot(None))
        ai_indexed_count = (await self.session.execute(ai_indexed_stmt)).scalar() or 0

        # Color stats aggregation
        color_stmt = (
            select(Wallpaper.dominant_color, func.count(Wallpaper.id))
            .where(Wallpaper.dominant_color.isnot(None))
            .group_by(Wallpaper.dominant_color)
            .order_by(func.count(Wallpaper.id).desc())
            .limit(10)
        )
        color_rows = (await self.session.execute(color_stmt)).all()
        color_stats = [
            ColorStat(name=row[0], hex=row[0], count=row[1])
            for row in color_rows
        ]

        popular_searches = [
            "8K Ultra",
            "Cyberpunk City",
            "Deep Space Nebula",
            "AMOLED Dark Minimalist",
            "Anime Landscape",
            "Cosmic Supernova",
            "Tropical Nature",
            "Supercars 8K",
        ]

        return SearchAnalyticsResponse(
            total_wallpapers=total_count,
            ai_indexed_wallpapers=ai_indexed_count,
            color_distribution=color_stats,
            popular_searches=popular_searches,
        )

    async def get_suggestions(self, query: Optional[str] = None, limit: int = 10) -> SearchSuggestionsResponse:
        """Returns popular searches, suggested tags, and suggested categories."""
        cat_stmt = (
            select(Category.name)
            .where(Category.is_active.is_(True))
            .order_by(Category.sort_order.asc(), Category.name.asc())
            .limit(limit)
        )
        cat_result = await self.session.execute(cat_stmt)
        categories = list(cat_result.scalars().all())

        tag_stmt = select(Tag.name).order_by(Tag.name.asc()).limit(limit)
        if query and query.strip():
            tag_stmt = (
                select(Tag.name)
                .where(Tag.name.ilike(f"%{query.strip()}%"))
                .order_by(Tag.name.asc())
                .limit(limit)
            )
        tag_result = await self.session.execute(tag_stmt)
        tags = list(tag_result.scalars().all())

        popular_searches = [
            "8K Ultra",
            "Cyberpunk City",
            "Deep Space Nebula",
            "AMOLED Dark Minimalist",
            "Anime Landscape",
            "Cosmic Supernova",
            "Tropical Nature",
            "Supercars 8K",
        ]

        return SearchSuggestionsResponse(
            query=query,
            popular_searches=popular_searches,
            suggested_tags=tags,
            suggested_categories=categories
        )
