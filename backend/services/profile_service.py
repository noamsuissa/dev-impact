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
from utils.auth_utils import get_supabase_client
from services.user_service import UserService
from services.project_service import ProjectService
from schemas.profile import (
    PublishProfileResponse,
    CheckUsernameResponse,
    ProfileResponse,
)
from schemas.auth import MessageResponse

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
    def generate_slug(name: str) -> str:
        """Generate URL-friendly slug from profile name"""
        if not name:
            return ""
        # Convert to lowercase, replace spaces and special chars with dashes
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower())
        # Remove leading/trailing dashes
        slug = slug.strip('-')
        # Ensure it's not empty
        if not slug:
            slug = "profile"
        return slug

    @staticmethod
    def validate_slug(slug: str) -> bool:
        """Validate slug format"""
        if not slug:
            return False
        # Lowercase alphanumeric and hyphens only, 1-100 characters
        pattern = r'^[a-z0-9-]{1,100}$'
        return bool(re.match(pattern, slug))

    @staticmethod
    async def publish_profile(username: str, profile_id: str, user_id: str, token: str) -> PublishProfileResponse:
        """
        Publish or update a user profile in Supabase
        
        Args:
            username: The user's username
            profile_id: The profile ID to publish
            user_id: The authenticated user's ID
            token: The user's auth token
            
        Returns:
            PublishProfileResponse with success status, username, profile_slug, and URL
        """
        try:
            if not ProfileService.validate_username(username):
                raise HTTPException(status_code=400, detail="Username must be 3-50 characters, lowercase letters, numbers, and hyphens only")
            
            # Ensure username consistency (lowercase)
            username = username.lower()
            
            supabase = get_supabase_client(access_token=token)
            
            # Verify profile exists and belongs to user
            profile_result = supabase.table("user_profiles")\
                .select("id, slug, name, description")\
                .eq("id", profile_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not profile_result.data:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            profile = profile_result.data
            profile_slug = profile["slug"]
            
            # Check if this profile is already published by another user (shouldn't happen, but check anyway)
            existing = supabase.table("published_profiles")\
                .select("user_id, profile_id")\
                .eq("username", username)\
                .eq("profile_slug", profile_slug)\
                .execute()
            
            if existing.data and len(existing.data) > 0:
                existing_profile = existing.data[0]
                # Check if it's a different user (shouldn't happen with proper auth, but safety check)
                if existing_profile.get("user_id") and existing_profile["user_id"] != user_id:
                    raise HTTPException(status_code=409, detail="This profile slug is already taken for this username")
            
            # Fetch latest user profile from database
            try:
                user_profile = await UserService.get_profile(user_id)
            except Exception as e:
                print(f"Error fetching user profile: {e}")
                raise HTTPException(status_code=500, detail="Failed to fetch user profile")
            
            # Fetch latest projects from database for this profile
            try:
                projects = await ProjectService.list_projects(user_id, profile_id=profile_id)
            except Exception as e:
                print(f"Error fetching projects: {e}")
                raise HTTPException(status_code=500, detail="Failed to fetch projects")
            
            # Build profile_data from fresh database data
            fresh_profile_data = {
                "user": {
                    "name": user_profile.get("full_name", ""),
                    "github": {
                        "username": user_profile.get("github_username"),
                        "avatar_url": user_profile.get("github_avatar_url")
                    } if user_profile.get("github_username") else None
                },
                "profile": {
                    "name": profile["name"],
                    "description": profile.get("description")
                },
                "projects": projects
            }
            
            # Check if profile is already published
            existing = supabase.table("published_profiles")\
                .select("id")\
                .eq("username", username)\
                .eq("profile_slug", profile_slug)\
                .execute()
            
            # Insert or update published profile with fresh data
            if existing.data and len(existing.data) > 0:
                # Update existing
                result = supabase.table("published_profiles")\
                    .update({
                        "profile_id": profile_id,
                        "profile_data": fresh_profile_data,
                        "is_published": True,
                        "updated_at": datetime.utcnow().isoformat()
                    })\
                    .eq("username", username)\
                    .eq("profile_slug", profile_slug)\
                    .execute()
            else:
                # Insert new
                result = supabase.table("published_profiles")\
                    .insert({
                        "user_id": user_id,  # Keep for backward compatibility
                        "username": username,
                        "profile_id": profile_id,
                        "profile_slug": profile_slug,
                        "profile_data": fresh_profile_data,
                        "is_published": True,
                        "updated_at": datetime.utcnow().isoformat()
                    })\
                    .execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to publish profile")
            
            # Get base domain from environment, default to dev-impact.io
            base_domain = os.getenv("BASE_DOMAIN", "dev-impact.io")
            
            # Generate URL: username.dev-impact.io/profile-slug
            url = f"https://{username}.{base_domain}/{profile_slug}"
            
            return PublishProfileResponse(
                success=True,
                username=username,
                profile_slug=profile_slug,
                url=url,
                message="Profile published successfully"
            )
        except HTTPException:
            # Propagate known exceptions without modification
            raise
        except Exception as e:
            print(f"Error in publish_profile: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while publishing the profile")

    @staticmethod
    async def get_profile(username: str, profile_slug: Optional[str] = None) -> ProfileResponse:
        """
        Get a published profile by username and optional profile slug
        
        Args:
            username: The profile username to fetch
            profile_slug: Optional profile slug (for multi-profile support)
            
        Returns:
            ProfileResponse containing profile data
        """
        try:
            if not ProfileService.validate_username(username):
                raise HTTPException(status_code=400, detail="Invalid username format")
            
            supabase = get_supabase_client()
            
            # Build query
            query = supabase.table("published_profiles")\
                .select("*")\
                .eq("username", username)\
                .eq("is_published", True)
            
            # If profile_slug is provided, filter by it
            # Otherwise, get the first published profile (backward compatibility)
            if profile_slug:
                if not ProfileService.validate_slug(profile_slug):
                    raise HTTPException(status_code=400, detail="Invalid profile slug format")
                query = query.eq("profile_slug", profile_slug)
            
            result = query.execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            # If no profile_slug provided, get the first one (backward compatibility)
            profile = result.data[0] if not profile_slug else result.data[0]
            
            # Increment view count
            try:
                update_query = supabase.table("published_profiles")\
                    .update({"view_count": profile["view_count"] + 1})\
                    .eq("username", username)
                
                if profile_slug:
                    update_query = update_query.eq("profile_slug", profile_slug)
                else:
                    update_query = update_query.eq("id", profile["id"])
                
                update_query.execute()
            except Exception as e:
                print(f"Failed to increment view count: {e}")
                raise HTTPException(status_code=500, detail="Failed to increment view count")
            
            # Return profile data
            profile_data = profile["profile_data"]
            return ProfileResponse(
                username=profile["username"],
                profile_slug=profile.get("profile_slug"),
                user=profile_data["user"],
                profile=profile_data.get("profile"),  # Profile name and description
                projects=profile_data["projects"],
                viewCount=profile["view_count"] + 1,
                publishedAt=profile["published_at"],
                updatedAt=profile["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in get_profile: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching the profile")

    @staticmethod
    async def unpublish_profile(username: str, profile_slug: str, user_id: str) -> MessageResponse:
        """
        Unpublish a profile
        
        Args:
            username: The profile username
            profile_slug: The profile slug to unpublish
            user_id: The authenticated user's ID
            
        Returns:
            MessageResponse with success status and message
        """
        try:
            supabase = get_supabase_client()
            
            # Verify ownership via profile_id
            result = supabase.table("published_profiles")\
                .select("profile_id, user_profiles!inner(user_id)")\
                .eq("username", username)\
                .eq("profile_slug", profile_slug)\
                .execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            # Check ownership via profile_id relationship
            profile_id = result.data[0].get("profile_id")
            if profile_id:
                profile_check = supabase.table("user_profiles")\
                    .select("user_id")\
                    .eq("id", profile_id)\
                    .single()\
                    .execute()
                
                if profile_check.data and profile_check.data["user_id"] != user_id:
                    raise HTTPException(status_code=403, detail="You don't have permission to unpublish this profile")
            
            # Unpublish (set is_published to false)
            supabase.table("published_profiles")\
                .update({"is_published": False})\
                .eq("username", username)\
                .eq("profile_slug", profile_slug)\
                .execute()
            
            return MessageResponse(
                success=True,
                message="Profile unpublished successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to unpublish profile: {e}")

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
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in list_profiles: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while listing the profiles")

    @staticmethod
    async def check_username(username: str) -> CheckUsernameResponse:
        """
        Check if a username is available
        
        Args:
            username: The username to check
            
        Returns:
            CheckUsernameResponse with availability status
        """
        try:
            if not ProfileService.validate_username(username):
                return CheckUsernameResponse(
                    available=False,
                    valid=False,
                    message="Username must be 3-50 characters, lowercase letters, numbers, and hyphens only"
                )
        
            supabase = get_supabase_client()
            
            # Use RPC call to check availability (checks format, reserved names, and existing profiles)
            result = supabase.rpc("is_username_available", {"desired_username": username}).execute()
            
            available = result.data
            
            return CheckUsernameResponse(
                available=available,
                valid=True,
                message="Username is available" if available else "Username is taken or reserved"
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error checking username: {e}")
            return CheckUsernameResponse(
                available=False,
                valid=True,
                message="Error checking username availability"
            )
