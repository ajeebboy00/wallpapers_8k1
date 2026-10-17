import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db, require_admin
from app.models.user import User
from app.schemas.collection import (
    CollectionCreate,
    CollectionDetailResponse,
    CollectionResponse,
    CollectionUpdate,
)
from app.schemas.common import PaginatedResponse, StandardResponse
from app.services.collection_service import CollectionService

router = APIRouter(prefix="/collections", tags=["Collections"])

@router.get(
    "",
    response_model=PaginatedResponse[CollectionResponse],
    status_code=status.HTTP_200_OK,
    summary="List published collections"
)
async def list_collections(
    pagination: PaginationParams = Depends(),
    is_featured: Optional[bool] = Query(None, description="Filter featured collections"),
    db: AsyncSession = Depends(get_db)
):
    service = CollectionService(db)
    return await service.list_collections(
        page=pagination.page,
        limit=pagination.limit,
        is_featured=is_featured,
        is_published=True
    )

@router.get(
    "/{slug_or_id}",
    response_model=StandardResponse[CollectionDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get collection details with wallpapers"
)
async def get_collection(
    slug_or_id: str,
    db: AsyncSession = Depends(get_db)
):
    service = CollectionService(db)
    coll = await service.get_collection(slug_or_id)
    return StandardResponse(
        success=True,
        data=coll,
        message="Collection details retrieved"
    )

@router.post(
    "",
    response_model=StandardResponse[CollectionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create collection (Admin only)"
)
async def create_collection(
    payload: CollectionCreate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CollectionService(db)
    created = await service.create_collection(payload)
    return StandardResponse(
        success=True,
        data=created,
        message="Collection created successfully"
    )

@router.put(
    "/{collection_id}",
    response_model=StandardResponse[CollectionResponse],
    status_code=status.HTTP_200_OK,
    summary="Update collection (Admin only)"
)
async def update_collection(
    collection_id: uuid.UUID,
    payload: CollectionUpdate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CollectionService(db)
    updated = await service.update_collection(collection_id, payload)
    return StandardResponse(
        success=True,
        data=updated,
        message="Collection updated successfully"
    )

@router.delete(
    "/{collection_id}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete collection (Admin only)"
)
async def delete_collection(
    collection_id: uuid.UUID,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CollectionService(db)
    await service.delete_collection(collection_id)
    return StandardResponse(
        success=True,
        data={"deleted": True, "collection_id": str(collection_id)},
        message="Collection deleted successfully"
    )
