"""
Subscription Router - Handle subscription and payment endpoints
"""
from fastapi import APIRouter, Depends
from backend.schemas.subscription import CheckoutSessionRequest, CheckoutSessionResponse, SubscriptionInfoResponse
from backend.schemas.auth import MessageResponse
from backend.services.stripe_service import StripeService
from backend.services.subscription_service import SubscriptionService
from backend.utils import auth_utils
from backend.utils.dependencies import ServiceDBClient

router = APIRouter(
    prefix="/api/subscriptions",
    tags=["subscriptions"],
)


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Create a Stripe Checkout session for Pro plan subscription
    
    Returns a checkout URL to redirect the user to Stripe's hosted checkout page.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    user_email = auth_utils.get_user_email_from_authorization(authorization)
    
    result = await StripeService.create_checkout_session(
        client,
        user_id=user_id,
        user_email=user_email,
        success_url=request.success_url,
        cancel_url=request.cancel_url
    )

    
    return CheckoutSessionResponse(
        checkout_url=result["checkout_url"],
        session_id=result["session_id"]
    )


@router.get("/info", response_model=SubscriptionInfoResponse)
async def get_subscription_info(
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Get user's subscription information and profile limits
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    info = await SubscriptionService.get_subscription_info(client, user_id)
    return info


@router.post("/cancel", response_model=MessageResponse)
async def cancel_subscription(
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Cancel subscription
    
    Cancels the user's subscription at the end of the current billing period.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await SubscriptionService.cancel_subscription(client, user_id)
    return result