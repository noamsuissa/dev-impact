"""
User Router - Handle user profile endpoints
"""
from fastapi import APIRouter, HTTPException, Header, Request
from typing import Optional
from schemas.user import UserProfile, UpdateProfileRequest, OnboardingRequest
from services.user_service import UserService
from services.auth_service import AuthService

router = APIRouter(
    prefix="/api/user",
    tags=["user"],
)


async def get_user_id_from_header(authorization: Optional[str]) -> str:
    """Extract and validate user ID from authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    access_token = authorization.replace("Bearer ", "")
    user_id = await AuthService.verify_token(access_token)
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return user_id


@router.get("/profile", response_model=UserProfile)
async def get_profile(authorization: Optional[str] = Header(None)):
    """
    Get current user's profile
    
    Returns the authenticated user's profile data.
    """
    user_id = await get_user_id_from_header(authorization)
    
    try:
        profile = await UserService.get_profile(user_id)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get profile error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch profile"
        )


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    request: UpdateProfileRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Update current user's profile
    
    Updates the authenticated user's profile data.
    """
    user_id = await get_user_id_from_header(authorization)
    
    try:
        profile_data = request.model_dump(exclude_none=True)
        profile = await UserService.update_profile(user_id, profile_data)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update profile error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update profile"
        )


@router.post("/onboarding", response_model=UserProfile)
async def complete_onboarding(
    request: OnboardingRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Complete user onboarding
    
    Creates or updates user profile with onboarding data.
    """
    user_id = await get_user_id_from_header(authorization)
    
    try:
        profile_data = {
            "username": request.username,
            "full_name": request.name,
            "github_username": request.github.username if request.github else None,
            "github_avatar_url": request.github.avatar_url if request.github else None,
        }
        
        profile = await UserService.create_or_update_profile(user_id, profile_data)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        print(f"Onboarding error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to complete onboarding"
        )


@router.delete("/account")
async def delete_account(authorization: Optional[str] = Header(None)):
    """
    Delete current user's account
    
    Permanently deletes the user's profile and authentication account.
    This action cannot be undone.
    """
    user_id = await get_user_id_from_header(authorization)
    
    try:
        result = await UserService.delete_account(user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete account error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete account"
        )

