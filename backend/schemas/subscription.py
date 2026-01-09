"""
Subscription Schemas - Pydantic models for subscription operations
"""

from datetime import datetime

from pydantic import BaseModel


class CheckoutSessionRequest(BaseModel):
    """Request model for creating a Stripe checkout session"""

    success_url: str
    cancel_url: str
    billing_period: str = "monthly"  # "monthly" or "yearly"


class CheckoutSessionResponse(BaseModel):
    """Response model containing checkout session URL"""

    checkout_url: str
    session_id: str


class SubscriptionInfoResponse(BaseModel):
    """Subscription info response schema"""

    subscription_type: str
    subscription_status: str | None = None
    cancel_at_period_end: bool = False
    current_period_end: datetime | None = None
    portfolio_count: int
    max_portfolios: int
    can_add_portfolio: bool
    project_count: int
    max_projects: int
    can_add_project: bool
