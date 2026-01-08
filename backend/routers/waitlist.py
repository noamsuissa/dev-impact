"""
Waitlist Router - Handle waitlist endpoints
"""

from fastapi import APIRouter
from backend.schemas.waitlist import WaitlistSignupRequest, WaitlistResponse
from backend.core.container import ServiceDBClient, WaitlistServiceDep

router = APIRouter(
    prefix="/api/waitlist",
    tags=["waitlist"],
)


@router.post("/signup", response_model=WaitlistResponse)
async def signup_waitlist(
    request: WaitlistSignupRequest,
    client: ServiceDBClient,
    waitlist_service: WaitlistServiceDep,
):
    """
    Sign up for the waitlist.

    Adds a user's email to the waitlist and sends a confirmation email.
    """
    result = await waitlist_service.signup(
        client, email=request.email, name=request.name
    )
    return result
