"""
Subscription Schemas - Pydantic models for subscription operations
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CheckoutSessionRequest(BaseModel):
    """Request model for creating a Stripe checkout session"""
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """Response model containing checkout session URL"""
    checkout_url: str
    session_id: str

class SubscriptionInfoResponse(BaseModel):
    subscription_type: str
    subscription_status: Optional[str] = None
    cancel_at_period_end: bool = False
    current_period_end: Optional[datetime] = None
    profile_count: int
    max_profiles: int
    can_add_profile: bool