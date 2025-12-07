"""
User Profiles Router - Handle user profile endpoints
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
from schemas.user_profile import UserProfile, CreateUserProfileRequest, UpdateUserProfileRequest
from services.user_profile_service import UserProfileService
from utils import auth_utils

router = APIRouter(
    prefix="/api/user-profiles",
    tags=["user-profiles"],
)

@router.post("", response_model=UserProfile)
async def create_user_profile(
    profile: CreateUserProfileRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Create a new user profile
    
    Creates a profile that can group related projects.
    """
    # Get user ID from token
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    token = authorization.replace("Bearer ", "")
    
    try:
        result = await UserProfileService.create_user_profile(
            user_id=user_id,
            name=profile.name,
            description=profile.description,
            token=token
        )
        return UserProfile(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating user profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create profile: {str(e)}"
        )

@router.get("", response_model=List[UserProfile])
async def list_user_profiles(
    authorization: Optional[str] = Header(None)
):
    """
    List all profiles for the authenticated user
    """
    # Get user ID from token
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    token = authorization.replace("Bearer ", "")
    
    try:
        profiles = await UserProfileService.list_user_profiles(user_id, token=token)
        return [UserProfile(**p) for p in profiles]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error listing user profiles: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list profiles: {str(e)}"
        )

@router.get("/{profile_id}", response_model=UserProfile)
async def get_user_profile(
    profile_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get a single user profile by ID
    """
    # Get user ID from token
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    token = authorization.replace("Bearer ", "")
    
    try:
        profile = await UserProfileService.get_user_profile(profile_id, user_id, token=token)
        return UserProfile(**profile)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch profile: {str(e)}"
        )

@router.put("/{profile_id}", response_model=UserProfile)
async def update_user_profile(
    profile_id: str,
    profile: UpdateUserProfileRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Update a user profile
    """
    # Get user ID from token
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    token = authorization.replace("Bearer ", "")
    
    try:
        result = await UserProfileService.update_user_profile(
            profile_id=profile_id,
            user_id=user_id,
            name=profile.name,
            description=profile.description,
            token=token
        )
        return UserProfile(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.delete("/{profile_id}")
async def delete_user_profile(
    profile_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Delete a user profile
    """
    # Get user ID from token
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    token = authorization.replace("Bearer ", "")
    
    try:
        result = await UserProfileService.delete_user_profile(profile_id, user_id, token=token)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting user profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete profile: {str(e)}"
        )
