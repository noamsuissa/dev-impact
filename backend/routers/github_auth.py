from fastapi import APIRouter
from backend.schemas.github_auth import (
    DeviceCodeResponse,
    PollRequest,
    GitHubUser,
    UserProfileRequest,
    TokenResponse,
)
from backend.services.github_service import GitHubService

router = APIRouter(prefix="/api/auth/github", tags=["GitHub OAuth"])


@router.post("/device/code", response_model=DeviceCodeResponse)
async def initiate_device_flow():
    """
    Initiate GitHub Device Flow authentication.
    Returns device code, user code, and verification URI for the user to authorize.
    """
    result = await GitHubService.initiate_device_flow()
    return result


@router.post("/device/poll", response_model=TokenResponse)
async def poll_device_token(request: PollRequest):
    """
    Poll for GitHub access token.
    Returns access token if user has authorized, otherwise returns pending status.
    """
    result = await GitHubService.poll_for_token(request.device_code)
        
    if result is None:
        # Still pending authorization
        return TokenResponse(status="pending")
        
    return result


@router.post("/user", response_model=GitHubUser)
async def get_user_profile(request: UserProfileRequest):
    """
    Get GitHub user profile using access token.
    Returns user's GitHub profile information.
    """
    user = await GitHubService.get_user_profile(request.access_token)
    return user

