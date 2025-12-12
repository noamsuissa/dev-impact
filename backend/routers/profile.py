"""
Profiles Router - Handle profile publishing and retrieval
"""
from fastapi import APIRouter, Header, Depends
from typing import Optional
from schemas.profile import (
    PublishProfileRequest, 
    PublishProfileResponse,
    CheckUsernameResponse,
    ProfileResponse,
    ListProfilesResponse,
)
from schemas.auth import MessageResponse
from services.profile_service import ProfileService
from utils import auth_utils

router = APIRouter(
    prefix="/api/profiles",
    tags=["profiles"],
)


@router.post("", response_model=PublishProfileResponse)
async def publish_profile(
    profile: PublishProfileRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Publish or update a user profile
    
    This endpoint creates or updates a published profile with a unique username.
    The profile will be accessible at {username}.{BASE_DOMAIN}
    """
    user_id = auth_utils.get_user_id_from_token(authorization)
    result = await ProfileService.publish_profile(username=profile.username, profile_id=profile.profile_id, user_id=user_id, token=authorization)
    return result


@router.get("/check/{username}", response_model=CheckUsernameResponse)
async def check_username(username: str):
    """
    Check if a username is available
    
    Returns whether the username is available and valid.
    This route must be defined before the generic /{username} route.
    """
    result = await ProfileService.check_username(username)
    return result


@router.get("/{username}/{profile_slug}", response_model=ProfileResponse)
async def get_profile_with_slug(username: str, profile_slug: str):
    """
    Get a published profile by username and profile slug
    
    This endpoint is public and doesn't require authentication.
    It increments the view count each time it's accessed.
    
    URL format: /api/profiles/{username}/{profile_slug}
    """
    profile = await ProfileService.get_profile(username, profile_slug)
    return profile

@router.get("/{username}", response_model=ProfileResponse)
async def get_profile(username: str):
    """
    Get a published profile by username (backward compatibility)
    
    This endpoint is public and doesn't require authentication.
    It increments the view count each time it's accessed.
    
    Returns the first published profile for the username (for backward compatibility).
    """
    profile = await ProfileService.get_profile(username, None)
    return profile


@router.delete("/{username}/{profile_slug}", response_model=MessageResponse)
async def unpublish_profile(
    username: str,
    profile_slug: str,
    authorization: Optional[str] = Header(None)
):
    """
    Unpublish a profile
    
    This endpoint removes the published profile or sets is_published to false.
    Only the profile owner can unpublish their profile.
    """
    # Get user ID from token
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    result = await ProfileService.unpublish_profile(username, profile_slug, user_id)
    return result


@router.get("", response_model=ListProfilesResponse)
async def list_profiles(limit: int = 50, offset: int = 0):
    """
    List all published profiles
    
    This is a public endpoint that returns a list of all published profiles.
    Useful for creating a directory or discovery feature.
    """
    result = await ProfileService.list_profiles(limit, offset)
    return result
