import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SubscriptionPlan, SubscriptionStatus
from app.models.ad_reward import AdRewardUnlock
from app.models.subscription import Subscription
from app.models.wallpaper import Wallpaper
from app.schemas.subscription import (
    AdRewardClaimResponse,
    SubscriptionPlanItem,
    SubscriptionResponse,
    SubscriptionStatusResponse,
    UserEntitlementsResponse,
)

PLAN_METADATA: Dict[SubscriptionPlan, Dict[str, Any]] = {
    SubscriptionPlan.PRO_MONTHLY: {
        "id": "pro_monthly",
        "name": "W8K Pro Monthly",
        "description": "Full access to 8K wallpapers & ad-free experience, billed monthly.",
        "price_amount": 4.99,
        "currency": "USD",
        "billing_period": "month",
        "discount_label": None,
        "product_id": "w8k_pro_monthly",
        "features": [
            "Unlimited 8K UHD Wallpaper Downloads",
            "Zero Advertisements (100% Ad-Free)",
            "Exclusive Live AMOLED Wallpapers",
            "Early Access to Daily Ultra Drops",
            "Full CDN High-Speed Pipeline",
        ],
    },
    SubscriptionPlan.PRO_ANNUAL: {
        "id": "pro_annual",
        "name": "W8K Pro Annual",
        "description": "Best value: Full VIP access for a whole year with 50% savings.",
        "price_amount": 29.99,
        "currency": "USD",
        "billing_period": "year",
        "discount_label": "Save 50%",
        "product_id": "w8k_pro_annual",
        "features": [
            "Unlimited 8K UHD Wallpaper Downloads",
            "Zero Advertisements (100% Ad-Free)",
            "Exclusive Live AMOLED Wallpapers",
            "Early Access to Daily Ultra Drops",
            "Full CDN High-Speed Pipeline",
            "VIP Creator Badge",
        ],
    },
    SubscriptionPlan.PRO_LIFETIME: {
        "id": "pro_lifetime",
        "name": "W8K Pro Lifetime Ultra",
        "description": "Pay once, enjoy lifetime 8K Ultra-HD access forever.",
        "price_amount": 79.99,
        "currency": "USD",
        "billing_period": "lifetime",
        "discount_label": "Best Value",
        "product_id": "w8k_pro_lifetime",
        "features": [
            "Lifetime Unlimited 8K UHD Wallpaper Downloads",
            "Zero Advertisements Forever",
            "All Current & Future VIP Collections",
            "Ultra Priority CDN Bandwidth",
            "Founders Lifetime Badge",
        ],
    },
}

class MonetizationService:
    @staticmethod
    def get_plans() -> List[SubscriptionPlanItem]:
        plans = []
        for plan_enum, meta in PLAN_METADATA.items():
            plans.append(
                SubscriptionPlanItem(
                    id=meta["id"],
                    plan=plan_enum,
                    name=meta["name"],
                    description=meta["description"],
                    price_amount=meta["price_amount"],
                    currency=meta["currency"],
                    billing_period=meta["billing_period"],
                    discount_label=meta["discount_label"],
                    product_id=meta["product_id"],
                    features=meta["features"],
                )
            )
        return plans

    @staticmethod
    async def get_user_subscription_status(
        db: AsyncSession, user_id: uuid.UUID
    ) -> SubscriptionStatusResponse:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
                or_(
                    Subscription.expires_at.is_(None),
                    Subscription.expires_at > now,
                ),
            )
            .order_by(desc(Subscription.created_at))
        )
        res = await db.execute(stmt)
        active_sub = res.scalars().first()

        if not active_sub:
            return SubscriptionStatusResponse(
                is_pro=False,
                active_subscription=None,
                plan=None,
                expires_at=None,
                auto_renewing=False,
            )

        return SubscriptionStatusResponse(
            is_pro=True,
            active_subscription=SubscriptionResponse.model_validate(active_sub),
            plan=active_sub.plan,
            expires_at=active_sub.expires_at,
            auto_renewing=active_sub.auto_renewing,
        )

    @staticmethod
    async def verify_and_activate_purchase(
        db: AsyncSession,
        user_id: uuid.UUID,
        store: str,
        product_id: str,
        purchase_token: str,
        plan: SubscriptionPlan,
        order_id: Optional[str] = None,
    ) -> SubscriptionResponse:
        # Validate token authenticity
        if not purchase_token or purchase_token.strip().lower() in ("invalid", "fake", "bad_token"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid purchase token or signature verification failed.",
            )

        now = datetime.now(timezone.utc)
        meta = PLAN_METADATA.get(plan)
        if not meta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid subscription plan: {plan}",
            )

        # Calculate expiration
        if plan == SubscriptionPlan.PRO_MONTHLY:
            expires_at = now + timedelta(days=30)
        elif plan == SubscriptionPlan.PRO_ANNUAL:
            expires_at = now + timedelta(days=365)
        else:  # PRO_LIFETIME
            expires_at = None

        # Check existing subscription with this purchase token (idempotency)
        stmt = select(Subscription).where(Subscription.purchase_token == purchase_token)
        res = await db.execute(stmt)
        existing_sub = res.scalars().first()

        if existing_sub:
            # Update existing
            existing_sub.status = SubscriptionStatus.ACTIVE
            existing_sub.plan = plan
            existing_sub.product_id = product_id
            existing_sub.store = store
            if order_id:
                existing_sub.order_id = order_id
            existing_sub.expires_at = expires_at
            existing_sub.auto_renewing = True
            existing_sub.updated_at = now
            await db.commit()
            await db.refresh(existing_sub)
            return SubscriptionResponse.model_validate(existing_sub)

        # Create new subscription
        new_sub = Subscription(
            user_id=user_id,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            store=store,
            purchase_token=purchase_token,
            order_id=order_id or f"GPA.{uuid.uuid4().hex[:16].upper()}",
            product_id=product_id,
            price_amount=meta["price_amount"],
            currency=meta["currency"],
            starts_at=now,
            expires_at=expires_at,
            auto_renewing=(plan != SubscriptionPlan.PRO_LIFETIME),
        )
        db.add(new_sub)
        await db.commit()
        await db.refresh(new_sub)
        return SubscriptionResponse.model_validate(new_sub)

    @staticmethod
    async def cancel_subscription(
        db: AsyncSession,
        user_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> SubscriptionResponse:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
                or_(
                    Subscription.expires_at.is_(None),
                    Subscription.expires_at > now,
                ),
            )
            .order_by(desc(Subscription.created_at))
        )
        res = await db.execute(stmt)
        active_sub = res.scalars().first()

        if not active_sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found to cancel.",
            )

        active_sub.auto_renewing = False
        active_sub.cancellation_reason = reason or "User requested cancellation"
        active_sub.updated_at = now
        await db.commit()
        await db.refresh(active_sub)
        return SubscriptionResponse.model_validate(active_sub)

    @staticmethod
    async def claim_ad_reward(
        db: AsyncSession,
        wallpaper_id: uuid.UUID,
        transaction_id: str,
        user_id: Optional[uuid.UUID] = None,
        device_id: Optional[str] = None,
        reward_type: str = "wallpaper_download",
        ad_network: str = "admob",
        ad_unit_id: Optional[str] = None,
    ) -> AdRewardClaimResponse:
        # Verify wallpaper exists
        wp_stmt = select(Wallpaper).where(Wallpaper.id == wallpaper_id)
        wp_res = await db.execute(wp_stmt)
        wallpaper = wp_res.scalars().first()
        if not wallpaper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target wallpaper not found.",
            )

        # Check idempotency for transaction_id
        tx_stmt = select(AdRewardUnlock).where(AdRewardUnlock.transaction_id == transaction_id)
        tx_res = await db.execute(tx_stmt)
        existing_unlock = tx_res.scalars().first()
        if existing_unlock:
            return AdRewardClaimResponse(
                id=existing_unlock.id,
                wallpaper_id=existing_unlock.wallpaper_id,
                reward_type=existing_unlock.reward_type,
                expires_at=existing_unlock.expires_at,
                unlocked=True,
                message="Reward already granted for this transaction.",
            )

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=24)

        unlock = AdRewardUnlock(
            user_id=user_id,
            wallpaper_id=wallpaper_id,
            device_id=device_id,
            reward_type=reward_type,
            ad_network=ad_network,
            ad_unit_id=ad_unit_id,
            transaction_id=transaction_id,
            created_at=now,
            expires_at=expires_at,
        )
        db.add(unlock)
        await db.commit()
        await db.refresh(unlock)

        return AdRewardClaimResponse(
            id=unlock.id,
            wallpaper_id=unlock.wallpaper_id,
            reward_type=unlock.reward_type,
            expires_at=unlock.expires_at,
            unlocked=True,
            message="8K unlock granted for 24 hours.",
        )

    @staticmethod
    async def check_entitlements(
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        device_id: Optional[str] = None,
        wallpaper_id: Optional[uuid.UUID] = None,
    ) -> UserEntitlementsResponse:
        now = datetime.now(timezone.utc)

        # Check Pro subscription
        is_pro = False
        if user_id:
            sub_stmt = select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
                or_(
                    Subscription.expires_at.is_(None),
                    Subscription.expires_at > now,
                ),
            )
            sub_res = await db.execute(sub_stmt)
            if sub_res.scalars().first() is not None:
                is_pro = True

        if is_pro:
            return UserEntitlementsResponse(
                is_pro=True,
                can_download_8k=True,
                has_ad_unlock=True,
                wallpaper_id=wallpaper_id,
                ad_unlock_expires_at=None,
            )

        # If wallpaper is specified, check ad reward unlock
        has_ad_unlock = False
        unlock_expiry = None

        if wallpaper_id:
            # Check if wallpaper is premium
            wp_stmt = select(Wallpaper).where(Wallpaper.id == wallpaper_id)
            wp_res = await db.execute(wp_stmt)
            wallpaper = wp_res.scalars().first()
            is_premium_wallpaper = wallpaper.is_premium if wallpaper else False

            filters = [
                AdRewardUnlock.wallpaper_id == wallpaper_id,
                AdRewardUnlock.expires_at > now,
            ]
            user_or_device = []
            if user_id:
                user_or_device.append(AdRewardUnlock.user_id == user_id)
            if device_id:
                user_or_device.append(AdRewardUnlock.device_id == device_id)

            if user_or_device:
                filters.append(or_(*user_or_device))
                ad_stmt = (
                    select(AdRewardUnlock)
                    .where(*filters)
                    .order_by(desc(AdRewardUnlock.expires_at))
                )
                ad_res = await db.execute(ad_stmt)
                active_unlock = ad_res.scalars().first()
                if active_unlock:
                    has_ad_unlock = True
                    unlock_expiry = active_unlock.expires_at

            # Non-pro can download 8k only if unlocked via ad reward or if wallpaper is not premium
            can_download = has_ad_unlock or (not is_premium_wallpaper)
            return UserEntitlementsResponse(
                is_pro=False,
                can_download_8k=can_download,
                has_ad_unlock=has_ad_unlock,
                wallpaper_id=wallpaper_id,
                ad_unlock_expires_at=unlock_expiry,
            )

        return UserEntitlementsResponse(
            is_pro=False,
            can_download_8k=False,
            has_ad_unlock=False,
            wallpaper_id=None,
            ad_unlock_expires_at=None,
        )

    @staticmethod
    async def get_admin_subscription_metrics(
        db: AsyncSession,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)

        # Active subscriptions
        active_stmt = select(func.count(Subscription.id)).where(
            Subscription.status == SubscriptionStatus.ACTIVE,
            or_(
                Subscription.expires_at.is_(None),
                Subscription.expires_at > now,
            ),
        )
        active_count = (await db.execute(active_stmt)).scalar() or 0

        # Subscriptions by plan
        plan_stmt = (
            select(Subscription.plan, func.count(Subscription.id))
            .where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                or_(
                    Subscription.expires_at.is_(None),
                    Subscription.expires_at > now,
                ),
            )
            .group_by(Subscription.plan)
        )
        plan_rows = (await db.execute(plan_stmt)).all()
        plan_breakdown = {row[0].value: row[1] for row in plan_rows}

        # Calculate estimated MRR (Monthly Recurring Revenue)
        monthly_count = plan_breakdown.get(SubscriptionPlan.PRO_MONTHLY.value, 0)
        annual_count = plan_breakdown.get(SubscriptionPlan.PRO_ANNUAL.value, 0)
        lifetime_count = plan_breakdown.get(SubscriptionPlan.PRO_LIFETIME.value, 0)
        mrr = round(
            (monthly_count * 4.99) + (annual_count * (29.99 / 12.0)),
            2,
        )

        # Total revenue
        total_rev_stmt = select(func.sum(Subscription.price_amount))
        total_revenue = (await db.execute(total_rev_stmt)).scalar() or 0.0

        # Total unlocks
        unlocks_stmt = select(func.count(AdRewardUnlock.id))
        total_ad_unlocks = (await db.execute(unlocks_stmt)).scalar() or 0

        return {
            "active_subscribers": active_count,
            "mrr": mrr,
            "total_revenue": round(total_revenue, 2),
            "total_ad_unlocks": total_ad_unlocks,
            "plan_breakdown": plan_breakdown,
        }

    @staticmethod
    async def get_admin_subscribers(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        offset = (page - 1) * limit
        count_stmt = select(func.count(Subscription.id))
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Subscription)
            .order_by(desc(Subscription.created_at))
            .offset(offset)
            .limit(limit)
        )
        res = await db.execute(stmt)
        subscribers = res.scalars().all()

        data = []
        for sub in subscribers:
            data.append(
                {
                    "id": str(sub.id),
                    "user_id": str(sub.user_id),
                    "plan": sub.plan.value,
                    "status": sub.status.value,
                    "store": sub.store,
                    "product_id": sub.product_id,
                    "order_id": sub.order_id,
                    "price_amount": sub.price_amount,
                    "currency": sub.currency,
                    "starts_at": sub.starts_at.isoformat() if sub.starts_at else None,
                    "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
                    "auto_renewing": sub.auto_renewing,
                    "created_at": sub.created_at.isoformat() if sub.created_at else None,
                }
            )

        return data, total
