from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.subscription import (
    SubscriptionCancelRequest,
    SubscriptionPlanItem,
    SubscriptionResponse,
    SubscriptionStatusResponse,
    SubscriptionVerifyRequest,
)
from app.services.monetization_service import MonetizationService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.get(
    "/plans",
    response_model=StandardResponse[List[SubscriptionPlanItem]],
    summary="Get available subscription tiers",
)
async def get_subscription_plans():
    """Returns available monetization plans, prices, and premium features."""
    plans = MonetizationService.get_plans()
    return StandardResponse(
        success=True,
        data=plans,
        message="Available subscription tiers retrieved successfully",
    )

@router.get(
    "/status",
    response_model=StandardResponse[SubscriptionStatusResponse],
    summary="Get current user Pro subscription status",
)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns active subscription details and Pro status for the authenticated user."""
    status_info = await MonetizationService.get_user_subscription_status(db, current_user.id)
    return StandardResponse(
        success=True,
        data=status_info,
        message="Subscription status retrieved successfully",
    )

@router.post(
    "/verify",
    response_model=StandardResponse[SubscriptionResponse],
    status_code=status.HTTP_200_OK,
    summary="Verify store purchase receipt and activate Pro",
)
async def verify_purchase(
    payload: SubscriptionVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verifies Google Play or App Store purchase tokens, activates Pro subscription tier, and handles renewals."""
    subscription = await MonetizationService.verify_and_activate_purchase(
        db=db,
        user_id=current_user.id,
        store=payload.store,
        product_id=payload.product_id,
        purchase_token=payload.purchase_token,
        plan=payload.plan,
        order_id=payload.order_id,
    )
    return StandardResponse(
        success=True,
        data=subscription,
        message="Subscription verified and activated successfully",
    )

@router.post(
    "/cancel",
    response_model=StandardResponse[SubscriptionResponse],
    summary="Cancel subscription auto-renewal",
)
async def cancel_subscription(
    payload: SubscriptionCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancels auto-renewal for the user's active subscription while keeping benefits until the expiration date."""
    cancelled = await MonetizationService.cancel_subscription(
        db=db,
        user_id=current_user.id,
        reason=payload.reason,
    )
    return StandardResponse(
        success=True,
        data=cancelled,
        message="Subscription auto-renewal has been cancelled",
    )
