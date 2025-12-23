"""
User Router - Handle user profile endpoints
"""
from fastapi import APIRouter, Depends
from backend.schemas.user import UserProfile, UpdateProfileRequest, OnboardingRequest, CheckUsernameResponse
from backend.schemas.auth import MessageResponse
from backend.services.user_service import UserService
from backend.utils import auth_utils
from backend.utils.dependencies import ServiceDBClient

router = APIRouter(
    prefix="/api/user",
    tags=["user"],
)


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Get current user's profile
    
    Returns the authenticated user's profile data.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    profile = await UserService.get_profile(client, user_id)
    return profile


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    request: UpdateProfileRequest,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Update current user's profile
    
    Updates the authenticated user's profile data.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    profile_data = request.model_dump(exclude_none=True)
    profile = await UserService.update_profile(client, user_id, profile_data)
    return profile


@router.post("/onboarding", response_model=UserProfile)
async def complete_onboarding(
    request: OnboardingRequest,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Complete user onboarding
    
    Creates or updates user profile with onboarding data.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    profile_data = {
        "username": request.username,
        "full_name": request.name,
        "github_username": request.github.username if request.github else None,
        "github_avatar_url": request.github.avatar_url if request.github else None,
    }
    profile = await UserService.create_or_update_profile(client, user_id, profile_data)
    return profile


@router.get("/check-username/{username}", response_model=CheckUsernameResponse)
async def check_username(username: str, client: ServiceDBClient):
    """
    Check if a username is available for publishing portfolios
    
    Returns whether the username is available and valid.
    This is a public endpoint that doesn't require authentication.
    """
    result = await UserService.check_username(client, username)
    return result


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Delete current user's account
    
    Permanently deletes the user's profile and authentication account.
    This action cannot be undone.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    result = await UserService.delete_account(client, user_id)
    return result
