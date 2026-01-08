"""
Stripe Webhook Router
"""
from fastapi import APIRouter, Header, Request, HTTPException
from backend.core.container import ServiceDBClient, StripeClientDep

router = APIRouter(
    prefix="/api/webhooks",
    tags=["webhooks"],
)

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    client: ServiceDBClient,
    stripe_client: StripeClientDep,
    stripe_signature: str = Header(None)
):
    """
    Handle incoming Stripe webhooks
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    # Get raw body for signature verification
    payload = await request.body()

    await stripe_client.handle_webhook_event(client, payload, stripe_signature)

    return {"status": "success"}
