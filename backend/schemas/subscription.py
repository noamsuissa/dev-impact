"""
Subscription Schemas - Pydantic models for subscription operations
"""
from pydantic import BaseModel, HttpUrl


class CheckoutSessionRequest(BaseModel):
    """Request model for creating a Stripe checkout session"""
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """Response model containing checkout session URL"""
    checkout_url: str
    session_id: str
