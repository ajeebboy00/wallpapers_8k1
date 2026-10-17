import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import SubscriptionPlan, SubscriptionStatus

class SubscriptionPlanItem(BaseModel):
    id: str
    plan: SubscriptionPlan
    name: str
    description: str
    price_amount: float
    currency: str = "USD"
    billing_period: str
    discount_label: Optional[str] = None
    product_id: str
    features: List[str] = []

class SubscriptionPlansResponse(BaseModel):
    plans: List[SubscriptionPlanItem]

class SubscriptionVerifyRequest(BaseModel):
    store: str = Field(default="google_play", description="Store name: google_play or app_store")
    product_id: str = Field(..., description="Product ID from the store")
    purchase_token: str = Field(..., description="Purchase token or transaction receipt")
    order_id: Optional[str] = Field(None, description="Store order ID")
    plan: SubscriptionPlan = Field(..., description="Subscription plan selected")

class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    plan: SubscriptionPlan
    status: SubscriptionStatus
    store: str
    order_id: Optional[str] = None
    product_id: Optional[str] = None
    price_amount: float
    currency: str
    starts_at: datetime
    expires_at: Optional[datetime] = None
    auto_renewing: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SubscriptionStatusResponse(BaseModel):
    is_pro: bool
    active_subscription: Optional[SubscriptionResponse] = None
    plan: Optional[SubscriptionPlan] = None
    expires_at: Optional[datetime] = None
    auto_renewing: bool = False

class SubscriptionCancelRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Optional cancellation reason")

class AdRewardClaimRequest(BaseModel):
    wallpaper_id: uuid.UUID
    device_id: Optional[str] = None
    reward_type: str = "wallpaper_download"
    ad_network: str = "admob"
    ad_unit_id: Optional[str] = None
    transaction_id: str

class AdRewardClaimResponse(BaseModel):
    id: uuid.UUID
    wallpaper_id: uuid.UUID
    reward_type: str
    expires_at: datetime
    unlocked: bool = True
    message: str

class UserEntitlementsResponse(BaseModel):
    is_pro: bool
    can_download_8k: bool
    has_ad_unlock: bool
    wallpaper_id: Optional[uuid.UUID] = None
    ad_unlock_expires_at: Optional[datetime] = None
