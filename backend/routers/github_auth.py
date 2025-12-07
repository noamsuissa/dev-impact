from fastapi import APIRouter, HTTPException
from schemas.github_auth import (
    DeviceCodeResponse,
    PollRequest,
    GitHubUser,
    UserProfileRequest,
    TokenResponse,
)
from services.github_service import GitHubService

router = APIRouter(prefix="/api/auth/github", tags=["GitHub OAuth"])


@router.post("/device/code", response_model=DeviceCodeResponse)
async def initiate_device_flow():
    """
    Initiate GitHub Device Flow authentication.
    Returns device code, user code, and verification URI for the user to authorize.
    """
    try:
        result = await GitHubService.initiate_device_flow()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate device flow: {str(e)}")


@router.post("/device/poll", response_model=TokenResponse)
async def poll_device_token(request: PollRequest):
    """
    Poll for GitHub access token.
    Returns access token if user has authorized, otherwise returns pending status.
    """
    try:
        result = await GitHubService.poll_for_token(request.device_code)
        
        if result is None:
            # Still pending authorization
            return TokenResponse(status="pending")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/user", response_model=GitHubUser)
async def get_user_profile(request: UserProfileRequest):
    """
    Get GitHub user profile using access token.
    Returns user's GitHub profile information.
    """
    try:
        user = await GitHubService.get_user_profile(request.access_token)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch user profile: {str(e)}")

