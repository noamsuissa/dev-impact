"""
Profiles Router - Handle profile publishing and retrieval
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from schemas.profile import (
    PublishProfileRequest, 
    PublishProfileResponse,
)
from services.profile_service import ProfileService
from utils import auth_utils

router = APIRouter(
    prefix="/api/profiles",
    tags=["profiles"],
)





@router.post("", response_model=PublishProfileResponse)
async def publish_profile(
    profile: PublishProfileRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Publish or update a user profile
    
    This endpoint creates or updates a published profile with a unique username.
    The profile will be accessible at {username}.{BASE_DOMAIN}
    """
    # Validate authorization and extract user ID
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required to publish profile"
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = ProfileService.get_user_id_from_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    
    try:
        # Publish profile using service
        result = await ProfileService.publish_profile(
            username=profile.username,
            profile_id=profile.profile_id,
            user_id=user_id,
            token=token
        )
        
        return PublishProfileResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error publishing profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish profile: {str(e)}"
        )


@router.get("/check/{username}")
async def check_username(username: str):
    """
    Check if a username is available
    
    Returns whether the username is available and valid.
    This route must be defined before the generic /{username} route.
    """
    try:
        result = await ProfileService.check_username(username)
        return result
    except Exception as e:
        print(f"Error checking username: {e}")
        return {
            "available": False,
            "valid": True,
            "message": "Error checking username availability"
        }


@router.get("/{username}/{profile_slug}")
async def get_profile_with_slug(username: str, profile_slug: str):
    """
    Get a published profile by username and profile slug
    
    This endpoint is public and doesn't require authentication.
    It increments the view count each time it's accessed.
    
    URL format: /api/profiles/{username}/{profile_slug}
    """
    try:
        profile = await ProfileService.get_profile(username, profile_slug)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch profile: {str(e)}"
        )

@router.get("/{username}")
async def get_profile(username: str):
    """
    Get a published profile by username (backward compatibility)
    
    This endpoint is public and doesn't require authentication.
    It increments the view count each time it's accessed.
    
    Returns the first published profile for the username (for backward compatibility).
    """
    try:
        profile = await ProfileService.get_profile(username, None)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch profile: {str(e)}"
        )


@router.delete("/{username}/{profile_slug}")
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
    
    try:
        result = await ProfileService.unpublish_profile(username, profile_slug, user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error unpublishing profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unpublish profile: {str(e)}"
        )


@router.get("")
async def list_profiles(limit: int = 50, offset: int = 0):
    """
    List all published profiles
    
    This is a public endpoint that returns a list of all published profiles.
    Useful for creating a directory or discovery feature.
    """
    try:
        result = await ProfileService.list_profiles(limit, offset)
        return result
    except Exception as e:
        print(f"Error listing profiles: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list profiles: {str(e)}"
        )
