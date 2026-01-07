"""
Waitlist Router - Handle waitlist endpoints
"""
from fastapi import APIRouter
from backend.schemas.waitlist import WaitlistSignupRequest, WaitlistResponse
from backend.services.waitlist_service import WaitlistService
from backend.services.email_service import EmailService
from backend.utils.dependencies import ServiceDBClient

router = APIRouter(
    prefix="/api/waitlist",
    tags=["waitlist"],
)


@router.post("/signup", response_model=WaitlistResponse)
async def signup_waitlist(request: WaitlistSignupRequest, client: ServiceDBClient):
    """
    Sign up for the waitlist
    
    Adds a user's email to the waitlist and sends a confirmation email.
    """
    email_service = EmailService.get_instance()
    result = await WaitlistService.signup(
        client,
        email=request.email,
        email_service=email_service,
        name=request.name
    )
    return result

