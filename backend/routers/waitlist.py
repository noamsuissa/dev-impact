"""
Waitlist Router - Handle waitlist endpoints
"""
from fastapi import APIRouter
from schemas.waitlist import WaitlistSignupRequest, WaitlistResponse
from services.waitlist_service import WaitlistService

router = APIRouter(
    prefix="/api/waitlist",
    tags=["waitlist"],
)


@router.post("/signup", response_model=WaitlistResponse)
async def signup_waitlist(request: WaitlistSignupRequest):
    """
    Sign up for the waitlist
    
    Adds a user's email to the waitlist and sends a confirmation email.
    """
    result = await WaitlistService.signup(
        email=request.email,
        name=request.name
    )
    return result

