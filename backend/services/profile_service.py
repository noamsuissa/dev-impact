"""
Profile Service - Handle profile business logic and Supabase operations
"""
import os
import re
import jwt
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables
load_dotenv()


class ProfileService:
    """Service for handling profile operations with Supabase."""

    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        # Lowercase alphanumeric and hyphens only, 3-50 characters
        pattern = r'^[a-z0-9-]{3,50}$'
        return bool(re.match(pattern, username))

    @staticmethod
    def get_supabase_client(user_token: Optional[str] = None):
        """Get Supabase client from environment"""
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        # Try service role key first (for backend operations), fall back to anon key
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            print(f"DEBUG - SUPABASE_URL: {url}")
            print(f"DEBUG - Key available: {'Yes' if key else 'No'}")
            raise HTTPException(
                status_code=500,
                detail="Supabase configuration not found. Make sure SUPABASE_URL and keys are set in .env file"
            )
        
        client = create_client(url, key)
        
        # If a user token is provided and we're using anon key, set the auth header
        if user_token and not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
            client.postgrest.auth(user_token)
        
        return client

    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[str]:
        """Extract user ID from JWT token"""
        try:
            # Decode JWT without verification (we trust Supabase tokens)
            # In production, you should verify the signature with your Supabase JWT secret
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get('sub')
            return user_id
        except Exception as e:
            print(f"Error decoding token: {e}")
            return None

    @staticmethod
    async def publish_profile(
        username: str,
        profile_data: Dict[str, Any],
        user_id: str,
        token: str
    ) -> Dict[str, Any]:
        """
        Publish or update a user profile in Supabase
        
        Args:
            username: The desired username
            profile_data: The profile data containing user and projects
            user_id: The authenticated user's ID
            token: The user's auth token
            
        Returns:
            Dict with success status, username, and URL
        """
        if not ProfileService.validate_username(username):
            raise HTTPException(
                status_code=400,
                detail="Username must be 3-50 characters, lowercase letters, numbers, and hyphens only"
            )
        
        supabase = ProfileService.get_supabase_client(user_token=token)
        
        # Check if username is already taken by another user
        existing = supabase.table("published_profiles")\
            .select("user_id")\
            .eq("username", username)\
            .execute()
        
        if existing.data and len(existing.data) > 0:
            if existing.data[0]["user_id"] != user_id:
                raise HTTPException(
                    status_code=409,
                    detail="Username is already taken"
                )
        
        # Insert or update published profile
        result = supabase.table("published_profiles").upsert(
            {
                "user_id": user_id,
                "username": username,
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
        
        return {
            "success": True,
            "username": username,
            "url": f"https://dev-impact.io/{username}",
            "message": "Profile published successfully"
        }

    @staticmethod
    async def get_profile(username: str) -> Dict[str, Any]:
        """
        Get a published profile by username
        
        Args:
            username: The profile username to fetch
            
        Returns:
            Dict containing profile data
        """
        if not ProfileService.validate_username(username):
            raise HTTPException(
                status_code=400,
                detail="Invalid username format"
            )
        
        supabase = ProfileService.get_supabase_client()
        
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

    @staticmethod
    async def unpublish_profile(username: str, user_id: str) -> Dict[str, Any]:
        """
        Unpublish a profile
        
        Args:
            username: The profile username to unpublish
            user_id: The authenticated user's ID
            
        Returns:
            Dict with success status and message
        """
        supabase = ProfileService.get_supabase_client()
        
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

    @staticmethod
    async def list_profiles(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        List all published profiles
        
        Args:
            limit: Maximum number of profiles to return
            offset: Number of profiles to skip
            
        Returns:
            Dict containing profiles list and pagination info
        """
        supabase = ProfileService.get_supabase_client()
        
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

    @staticmethod
    async def check_username(username: str) -> Dict[str, Any]:
        """
        Check if a username is available
        
        Args:
            username: The username to check
            
        Returns:
            Dict with availability status
        """
        if not ProfileService.validate_username(username):
            return {
                "available": False,
                "valid": False,
                "message": "Username must be 3-50 characters, lowercase letters, numbers, and hyphens only"
            }
        
        try:
            supabase = ProfileService.get_supabase_client()
            
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

