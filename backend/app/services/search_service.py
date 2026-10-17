import math
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.search_repository import SearchRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.search import (
    AITaggingBatchResponse,
    SearchAnalyticsResponse,
    SearchFilterParams,
    SearchSuggestionsResponse,
    SimilarWallpaperItem,
    SimilarWallpapersResponse,
)
from app.schemas.wallpaper import WallpaperResponse

class SearchService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SearchRepository(session)

    async def search_wallpapers(
        self,
        params: SearchFilterParams
    ) -> PaginatedResponse[WallpaperResponse]:
        """Executes full-text, trigram fuzzy, and color-filtered search with complete pagination envelopes."""
        offset = (params.page - 1) * params.limit
        items, total = await self.repo.search_wallpapers(params, offset=offset, limit=params.limit)

        total_pages = math.ceil(total / params.limit) if total > 0 else 1
        meta = PaginationMeta(
            page=params.page,
            limit=params.limit,
            total=total,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_prev=params.page > 1
        )

        data = [WallpaperResponse.model_validate(item) for item in items]
        message = f"Found {total} wallpaper{'s' if total != 1 else ''} matching search criteria"

        return PaginatedResponse(
            success=True,
            data=data,
            meta=meta,
            message=message
        )

    async def get_similar_wallpapers(
        self,
        wallpaper_id: uuid.UUID,
        limit: int = 10,
    ) -> SimilarWallpapersResponse:
        """Finds visually and semantically similar wallpapers using multi-factor AI scoring."""
        scored_items = await self.repo.get_similar_wallpapers(wallpaper_id=wallpaper_id, limit=limit)
        similar_list = [
            SimilarWallpaperItem(
                wallpaper=WallpaperResponse.model_validate(item),
                similarity_score=score,
                matching_factors=factors,
            )
            for item, score, factors in scored_items
        ]
        return SimilarWallpapersResponse(
            source_wallpaper_id=wallpaper_id,
            similar=similar_list,
        )

    async def run_batch_ai_tagging(
        self,
        limit: int = 50,
        force_reprocess: bool = False,
        wallpaper_id: Optional[uuid.UUID] = None,
    ) -> AITaggingBatchResponse:
        """Executes automated AI vision analysis and color extraction across wallpapers."""
        processed = await self.repo.batch_process_ai_tagging(
            limit=limit,
            force_reprocess=force_reprocess,
            wallpaper_id=wallpaper_id,
        )
        return AITaggingBatchResponse(
            processed_count=len(processed),
            updated_wallpapers=[WallpaperResponse.model_validate(w) for w in processed],
            message=f"Successfully analyzed and AI-tagged {len(processed)} wallpaper{'s' if len(processed) != 1 else ''}.",
        )

    async def get_search_analytics(self) -> SearchAnalyticsResponse:
        """Retrieves search, index, and color palette analytics."""
        return await self.repo.get_search_analytics()

    async def get_suggestions(
        self,
        query: Optional[str] = None,
        limit: int = 10
    ) -> SearchSuggestionsResponse:
        """Retrieves popular search suggestions, trending tags, and category keywords."""
        return await self.repo.get_suggestions(query=query, limit=limit)
