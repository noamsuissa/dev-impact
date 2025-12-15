"""
User Profiles Router - Handle user profile endpoints
"""
from fastapi import APIRouter, Depends
from typing import List
from backend.schemas.user_profile import UserProfile, CreateUserProfileRequest, UpdateUserProfileRequest
from backend.services.user_profile_service import UserProfileService
from backend.utils import auth_utils
from backend.schemas.auth import MessageResponse

router = APIRouter(
    prefix="/api/user-profiles",
    tags=["user-profiles"],
)

@router.post("", response_model=UserProfile)
async def create_user_profile(
    profile: CreateUserProfileRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Create a new user profile
    
    Creates a profile that can group related projects.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await UserProfileService.create_user_profile(
        user_id=user_id,
        name=profile.name,
        description=profile.description,
        token=authorization
    )
    return result

@router.get("", response_model=List[UserProfile])
async def list_user_profiles(
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    List all profiles for the authenticated user
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    profiles = await UserProfileService.list_user_profiles(user_id, token=authorization)
    return profiles

@router.get("/{profile_id}", response_model=UserProfile)
async def get_user_profile(
    profile_id: str,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Get a single user profile by ID
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    profile = await UserProfileService.get_user_profile(profile_id, user_id, token=authorization)
    return profile

@router.put("/{profile_id}", response_model=UserProfile)
async def update_user_profile(
    profile_id: str,
    profile: UpdateUserProfileRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Update a user profile
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await UserProfileService.update_user_profile(profile_id, user_id, name=profile.name, description=profile.description, token=authorization)
    return result

@router.delete("/{profile_id}", response_model=MessageResponse)
async def delete_user_profile(
    profile_id: str,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Delete a user profile
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await UserProfileService.delete_user_profile(profile_id, user_id, token=authorization)
    return result
