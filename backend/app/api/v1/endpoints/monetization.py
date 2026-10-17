import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    PaginationParams,
    get_db,
    get_optional_user,
    require_admin,
)
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationMeta, StandardResponse
from app.schemas.subscription import (
    AdRewardClaimRequest,
    AdRewardClaimResponse,
    UserEntitlementsResponse,
)
from app.services.monetization_service import MonetizationService

router = APIRouter(prefix="/monetization", tags=["Monetization"])

@router.post(
    "/ad-reward",
    response_model=StandardResponse[AdRewardClaimResponse],
    status_code=status.HTTP_200_OK,
    summary="Claim 24-hour 8K wallpaper unlock via rewarded ad",
)
async def claim_ad_reward(
    payload: AdRewardClaimRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Grants 24 hours of 8K download entitlement for a specific wallpaper upon completion of a rewarded ad."""
    unlock = await MonetizationService.claim_ad_reward(
        db=db,
        wallpaper_id=payload.wallpaper_id,
        transaction_id=payload.transaction_id,
        user_id=current_user.id if current_user else None,
        device_id=payload.device_id,
        reward_type=payload.reward_type,
        ad_network=payload.ad_network,
        ad_unit_id=payload.ad_unit_id,
    )
    return StandardResponse(
        success=True,
        data=unlock,
        message="Rewarded ad unlock granted successfully",
    )

@router.get(
    "/entitlements",
    response_model=StandardResponse[UserEntitlementsResponse],
    summary="Check download and viewing entitlements",
)
async def check_entitlements(
    wallpaper_id: Optional[uuid.UUID] = Query(None, description="Wallpaper ID to check 8K unlock for"),
    device_id: Optional[str] = Query(None, description="Anonymous client device ID"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Determines if the requesting client has Pro status or a valid ad-reward unlock for full-resolution 8K assets."""
    entitlements = await MonetizationService.check_entitlements(
        db=db,
        user_id=current_user.id if current_user else None,
        device_id=device_id,
        wallpaper_id=wallpaper_id,
    )
    return StandardResponse(
        success=True,
        data=entitlements,
        message="Entitlements checked successfully",
    )

@router.get(
    "/admin/metrics",
    response_model=StandardResponse[Dict[str, Any]],
    summary="Admin monetization overview & MRR metrics",
)
async def get_admin_monetization_metrics(
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Returns subscription analytics, estimated MRR, total revenue, and subscriber counts."""
    metrics = await MonetizationService.get_admin_subscription_metrics(db)
    return StandardResponse(
        success=True,
        data=metrics,
        message="Monetization metrics retrieved successfully",
    )

@router.get(
    "/admin/subscribers",
    response_model=PaginatedResponse[Dict[str, Any]],
    summary="Admin subscriber ledger",
)
async def get_admin_subscribers_ledger(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Returns paginated subscribers ledger with billing details and plans."""
    subscribers, total = await MonetizationService.get_admin_subscribers(
        db=db,
        page=page,
        limit=limit,
    )
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    return PaginatedResponse(
        success=True,
        data=subscribers,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        ),
        message="Subscribers ledger retrieved successfully",
    )
