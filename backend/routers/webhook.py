"""
Stripe Webhook Router
"""
from fastapi import APIRouter, Header, Request, HTTPException
from backend.services.stripe_service import StripeService
from backend.utils.dependencies import ServiceDBClient

router = APIRouter(
    prefix="/api/webhooks",
    tags=["webhooks"],
)

@router.post("/stripe")
async def stripe_webhook(request: Request, client: ServiceDBClient, stripe_signature: str = Header(None)):
    """
    Handle incoming Stripe webhooks
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    
    # Get raw body for signature verification
    payload = await request.body()
    
    await StripeService.handle_webhook_event(client, payload, stripe_signature)
    
    return {"status": "success"}
