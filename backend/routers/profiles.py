"""
Profiles Router - Handle profile publishing and retrieval
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import re
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/api/profiles",
    tags=["profiles"],
)

# Pydantic models for request/response
class MetricData(BaseModel):
    primary: str
    label: str
    detail: Optional[str] = None

class ProjectData(BaseModel):
    id: str
    company: str
    projectName: str = Field(..., alias="projectName")
    role: str
    teamSize: Optional[int] = Field(None, alias="teamSize")
    problem: str
    contributions: List[str]
    techStack: List[str] = Field(..., alias="techStack")
    metrics: List[MetricData] = []

    class Config:
        populate_by_name = True

class GitHubData(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = Field(None, alias="avatar_url")

    class Config:
        populate_by_name = True

class UserData(BaseModel):
    name: str
    github: Optional[GitHubData] = None

class PublishProfileRequest(BaseModel):
    username: str
    user: UserData
    projects: List[ProjectData]

class PublishProfileResponse(BaseModel):
    success: bool
    username: str
    url: str
    message: str

class ProfileResponse(BaseModel):
    username: str
    user: UserData
    projects: List[ProjectData]
    viewCount: int = Field(..., alias="view_count")
    publishedAt: str = Field(..., alias="published_at")
    updatedAt: str = Field(..., alias="updated_at")

    class Config:
        populate_by_name = True

def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username:
        return False
    # Lowercase alphanumeric and hyphens only, 3-50 characters
    pattern = r'^[a-z0-9-]{3,50}$'
    return bool(re.match(pattern, username))

def get_supabase_client(user_token: Optional[str] = None):
    """Get Supabase client from environment"""
    from supabase import create_client, Client
    
    url = os.getenv("VITE_SUPABASE_URL")
    # Try service role key first (for backend operations), fall back to anon key
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print(f"DEBUG - VITE_SUPABASE_URL: {url}")
        print(f"DEBUG - Key available: {'Yes' if key else 'No'}")
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration not found. Make sure VITE_SUPABASE_URL and keys are set in .env file"
        )
    
    client = create_client(url, key)
    
    # If a user token is provided and we're using anon key, set the auth header
    if user_token and not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        client.postgrest.auth(user_token)
    
    return client

def get_user_id_from_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user ID from authorization token"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    try:
        import jwt
        # Decode JWT without verification (we trust Supabase tokens)
        # In production, you should verify the signature with your Supabase JWT secret
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get('sub')
        return user_id
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

@router.post("", response_model=PublishProfileResponse)
async def publish_profile(
    profile: PublishProfileRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Publish or update a user profile
    
    This endpoint creates or updates a published profile with a unique username.
    The profile will be accessible at dev-impact.io/{username}
    """
    # Validate username format
    if not validate_username(profile.username):
        raise HTTPException(
            status_code=400,
            detail="Username must be 3-50 characters, lowercase letters, numbers, and hyphens only"
        )
    
    # Get user ID and token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required to publish profile"
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    
    try:
        # Get Supabase client authenticated with user's token
        supabase = get_supabase_client(user_token=token)
        
        # Check if username is already taken by another user
        existing = supabase.table("published_profiles")\
            .select("user_id")\
            .eq("username", profile.username)\
            .execute()
        
        if existing.data and len(existing.data) > 0:
            if existing.data[0]["user_id"] != user_id:
                raise HTTPException(
                    status_code=409,
                    detail="Username is already taken"
                )
        
        # Prepare profile data
        profile_data = {
            "user": {
                "name": profile.user.name,
                "github": {
                    "username": profile.user.github.username if profile.user.github else None,
                    "avatar_url": profile.user.github.avatar_url if profile.user.github else None,
                }
            },
            "projects": [p.model_dump(by_alias=True) for p in profile.projects]
        }
        
        # Insert or update published profile
        # Use upsert with on_conflict to handle republishing
        result = supabase.table("published_profiles").upsert(
            {
                "user_id": user_id,
                "username": profile.username,
                "profile_data": profile_data,
                "is_published": True,
                "updated_at": datetime.utcnow().isoformat()
            },
            on_conflict="username"
        ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to publish profile"
            )
        
        return PublishProfileResponse(
            success=True,
            username=profile.username,
            url=f"https://dev-impact.io/{profile.username}",
            message="Profile published successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error publishing profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish profile: {str(e)}"
        )

@router.get("/{username}")
async def get_profile(username: str):
    """
    Get a published profile by username
    
    This endpoint is public and doesn't require authentication.
    It increments the view count each time it's accessed.
    """
    if not validate_username(username):
        raise HTTPException(
            status_code=400,
            detail="Invalid username format"
        )
    
    try:
        supabase = get_supabase_client()
        
        # Fetch published profile
        result = supabase.table("published_profiles")\
            .select("*")\
            .eq("username", username)\
            .eq("is_published", True)\
            .execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        
        profile = result.data[0]
        
        # Increment view count
        try:
            supabase.table("published_profiles")\
                .update({"view_count": profile["view_count"] + 1})\
                .eq("username", username)\
                .execute()
        except Exception as e:
            print(f"Failed to increment view count: {e}")
        
        # Return profile data
        profile_data = profile["profile_data"]
        return {
            "username": profile["username"],
            "user": profile_data["user"],
            "projects": profile_data["projects"],
            "view_count": profile["view_count"] + 1,
            "published_at": profile["published_at"],
            "updated_at": profile["updated_at"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch profile: {str(e)}"
        )

@router.delete("/{username}")
async def unpublish_profile(
    username: str,
    authorization: Optional[str] = Header(None)
):
    """
    Unpublish a profile
    
    This endpoint removes the published profile or sets is_published to false.
    Only the profile owner can unpublish their profile.
    """
    # Get user ID from token
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    try:
        supabase = get_supabase_client()
        
        # Verify ownership
        result = supabase.table("published_profiles")\
            .select("user_id")\
            .eq("username", username)\
            .execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        
        if result.data[0]["user_id"] != user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to unpublish this profile"
            )
        
        # Unpublish (set is_published to false)
        supabase.table("published_profiles")\
            .update({"is_published": False})\
            .eq("username", username)\
            .execute()
        
        return {
            "success": True,
            "message": "Profile unpublished successfully"
        }
    
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
        supabase = get_supabase_client()
        
        result = supabase.table("published_profiles")\
            .select("username, profile_data, view_count, published_at, updated_at")\
            .eq("is_published", True)\
            .order("published_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        profiles = []
        for profile in result.data:
            profile_data = profile["profile_data"]
            profiles.append({
                "username": profile["username"],
                "name": profile_data["user"]["name"],
                "github": profile_data["user"].get("github"),
                "projectCount": len(profile_data["projects"]),
                "viewCount": profile["view_count"],
                "publishedAt": profile["published_at"]
            })
        
        return {
            "profiles": profiles,
            "total": len(profiles),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        print(f"Error listing profiles: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list profiles: {str(e)}"
        )

@router.get("/check/{username}")
async def check_username(username: str):
    """
    Check if a username is available
    
    Returns whether the username is available and valid.
    """
    if not validate_username(username):
        return {
            "available": False,
            "valid": False,
            "message": "Username must be 3-50 characters, lowercase letters, numbers, and hyphens only"
        }
    
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("published_profiles")\
            .select("username")\
            .eq("username", username)\
            .execute()
        
        available = not result.data or len(result.data) == 0
        
        return {
            "available": available,
            "valid": True,
            "message": "Username is available" if available else "Username is taken"
        }
    
    except Exception as e:
        print(f"Error checking username: {e}")
        return {
            "available": False,
            "valid": True,
            "message": "Error checking username availability"
        }

