"""
Stripe Webhook Router
"""
from fastapi import APIRouter, Header, Request, HTTPException
from ..services.stripe_service import StripeService

router = APIRouter(
    prefix="/api/webhooks",
    tags=["webhooks"],
)

@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Handle incoming Stripe webhooks
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    
    # Get raw body for signature verification
    payload = await request.body()
    
    await StripeService.handle_webhook_event(payload, stripe_signature)
    
    return {"status": "success"}
