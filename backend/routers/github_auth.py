"""GitHub Auth Router - Handle GitHub authentication endpoints"""

from fastapi import APIRouter

from backend.core.container import GitHubClientDep
from backend.schemas.github_auth import (
    DeviceCodeResponse,
    GitHubUser,
    PollRequest,
    TokenResponse,
    UserProfileRequest,
)

router = APIRouter(prefix="/api/auth/github", tags=["GitHub OAuth"])


@router.post("/device/code", response_model=DeviceCodeResponse)
async def initiate_device_flow(github_client: GitHubClientDep):
    """Initiate GitHub Device Flow authentication.
    Returns device code, user code, and verification URI for the user to authorize.
    """
    result = await github_client.initiate_device_flow()
    return result


@router.post("/device/poll", response_model=TokenResponse)
async def poll_device_token(request: PollRequest, github_client: GitHubClientDep):
    """Poll for GitHub access token.
    Returns access token if user has authorized, otherwise returns pending status.
    """
    result = await github_client.poll_for_token(request.device_code)

    if result is None:
        # Still pending authorization
        return TokenResponse(status="pending")

    return result


@router.post("/user", response_model=GitHubUser)
async def get_user_profile(request: UserProfileRequest, github_client: GitHubClientDep):
    """Get GitHub user profile using access token.
    Returns user's GitHub profile information.
    """
    user = await github_client.get_user_profile(request.access_token)
    return user
