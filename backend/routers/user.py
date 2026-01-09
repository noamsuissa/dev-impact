"""User Router - Handle user profile endpoints
"""

from fastapi import APIRouter, Depends

from backend.core.container import ServiceDBClient, UserServiceDep
from backend.schemas.auth import MessageResponse
from backend.schemas.user import (
    CheckUsernameResponse,
    OnboardingRequest,
    UpdateProfileRequest,
    UserProfile,
)
from backend.utils import auth_utils

router = APIRouter(
    prefix="/api/user",
    tags=["user"],
)


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    client: ServiceDBClient,
    user_service: UserServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """Get current user's profile

    Returns the authenticated user's profile data.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)

    profile = await user_service.get_profile(client, user_id)
    return profile


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    request: UpdateProfileRequest,
    client: ServiceDBClient,
    user_service: UserServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """Update current user's profile

    Updates the authenticated user's profile data.
    Note: Setting a field to null will clear that field (e.g., disconnecting GitHub).
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)

    # Use exclude_unset=True instead of exclude_none=True
    # This allows explicitly set None values to be included (for clearing fields)
    # while excluding fields that weren't provided in the request
    profile_data = request.model_dump(exclude_unset=True)
    profile = await user_service.update_profile(client, user_id, profile_data)
    return profile


@router.post("/onboarding", response_model=UserProfile)
async def complete_onboarding(
    request: OnboardingRequest,
    client: ServiceDBClient,
    user_service: UserServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """Complete user onboarding

    Creates or updates user profile with onboarding data.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)

    profile_data = {
        "username": request.username,
        "full_name": request.name,
        "github_username": request.github.username if request.github else None,
        "github_avatar_url": request.github.avatar_url if request.github else None,
        "city": request.city,
        "country": request.country,
    }
    profile = await user_service.create_or_update_profile(client, user_id, profile_data)
    return profile


@router.get("/check-username/{username}", response_model=CheckUsernameResponse)
async def check_username(username: str, client: ServiceDBClient, user_service: UserServiceDep):
    """Check if a username is available for publishing portfolios

    Returns whether the username is available and valid.
    This is a public endpoint that doesn't require authentication.
    """
    result = await user_service.check_username(client, username)
    return result


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    client: ServiceDBClient,
    user_service: UserServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """Delete current user's account

    Permanently deletes the user's profile and authentication account.
    This action cannot be undone.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)

    result = await user_service.delete_account(client, user_id)
    return result
