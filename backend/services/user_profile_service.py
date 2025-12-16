"""
User Profile Service - Handle user profile operations with Supabase
"""
from typing import Optional, List
from fastapi import HTTPException
from backend.db.client import get_user_client
from backend.services.profile_service import ProfileService
from backend.services.subscription_service import SubscriptionService
from backend.schemas.user_profile import (
    UserProfile,
)
from backend.schemas.auth import MessageResponse

class UserProfileService:
    """Service for handling user profile operations with Supabase."""

    @staticmethod
    async def create_user_profile(
        user_id: str,
        name: str,
        description: Optional[str] = None,
        token: Optional[str] = None
    ) -> UserProfile:
        """
        Create a new user profile
        
        Args:
            user_id: The authenticated user's ID
            name: Profile name
            description: Optional profile description
            token: Optional user token for auth
            
        Returns:
            UserProfile containing created profile data
        """
        try:
            if not name or not name.strip():
                raise HTTPException(status_code=400, detail="Profile name is required")
            
            supabase = get_user_client(token)
            
            # Generate slug from name
            base_slug = ProfileService.generate_slug(name)
            slug = base_slug
            
            # Ensure slug is unique per user
            counter = 1
            while True:
                existing = supabase.table("user_profiles")\
                    .select("id")\
                    .eq("user_id", user_id)\
                    .eq("slug", slug)\
                    .execute()
                
                if not existing.data or len(existing.data) == 0:
                    break
                
                slug = f"{base_slug}-{counter}"
                counter += 1
                
                # Safety check to prevent infinite loop
                if counter > 1000:
                    raise HTTPException(status_code=500, detail="Failed to generate unique slug")
            
            # Check profile limit before creating
            subscription_info = await SubscriptionService.get_subscription_info(user_id, token)
            if not subscription_info.can_add_profile:
                raise HTTPException(
                    status_code=403,
                    detail=f"Profile limit reached. Free users are limited to {subscription_info.max_profiles} profiles. Upgrade to Pro for unlimited profiles."
                )
            
            # Get current profile count for display_order
            count_result = (supabase.table("user_profiles")
                .select("id", count="exact") # type: ignore[arg-type]
                .eq("user_id", user_id)
                .execute())
            
            display_order = len(count_result.data) if count_result.data else 0
            
            # Insert new profile
            result = supabase.table("user_profiles").insert({
                "user_id": user_id,
                "name": name.strip(),
                "description": description.strip() if description else None,
                "slug": slug,
                "display_order": display_order
            }).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=500, detail="Failed to create profile")
            
            profile = result.data[0]
            return UserProfile(
                id=profile["id"],
                name=profile["name"],
                description=profile.get("description"),
                slug=profile["slug"],
                display_order=profile["display_order"],
                created_at=profile["created_at"],
                updated_at=profile["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Create user profile error: {e}")
            raise HTTPException(status_code=500, detail="Failed to create user profile")

    @staticmethod
    async def list_user_profiles(
        user_id: str,
        token: Optional[str] = None
    ) -> List[UserProfile]:
        """
        List all profiles for a user
        
        Args:
            user_id: The user's ID
            token: Optional user token for auth
            
        Returns:
            List of UserProfile objects
        """
        try:
            supabase = get_user_client(token)
            
            result = supabase.table("user_profiles")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("display_order")\
                .order("created_at")\
                .execute()
            
            profiles = []
            for profile in result.data:
                profiles.append(UserProfile(
                    id=profile["id"],
                    name=profile["name"],
                    description=profile.get("description"),
                    slug=profile["slug"],
                    display_order=profile["display_order"],
                    created_at=profile["created_at"],
                    updated_at=profile["updated_at"]
                ))
            
            return profiles
        except HTTPException:
            raise
        except Exception as e:
            print(f"List user profiles error: {e}")
            raise HTTPException(status_code=500, detail="Failed to list user profiles")

    @staticmethod
    async def get_user_profile(
        profile_id: str,
        user_id: str,
        token: Optional[str] = None
    ) -> UserProfile:
        """
        Get a single user profile
        
        Args:
            profile_id: The profile ID
            user_id: The user's ID (for authorization)
            token: Optional user token for auth
            
        Returns:
            UserProfile object
        """
        try:
            supabase = get_user_client(token)
            
            result = supabase.table("user_profiles")\
                .select("*")\
                .eq("id", profile_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            profile = result.data
            return UserProfile(
                id=profile["id"],
                name=profile["name"],
                description=profile.get("description"),
                slug=profile["slug"],
                display_order=profile["display_order"],
                created_at=profile["created_at"],
                updated_at=profile["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get user profile error: {e}")
            raise HTTPException(status_code=500, detail="Failed to get user profile")

    @staticmethod
    async def update_user_profile(
        profile_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        token: Optional[str] = None
    ) -> UserProfile:
        """
        Update a user profile
        
        Args:
            profile_id: The profile ID
            user_id: The user's ID (for authorization)
            name: Optional new name
            description: Optional new description
            token: Optional user token for auth
            
        Returns:
            Updated UserProfile object
        """
        try:
            supabase = get_user_client(token)
            
            # Verify ownership
            existing = supabase.table("user_profiles")\
                .select("user_id, slug")\
                .eq("id", profile_id)\
                .execute()
            
            if not existing.data or len(existing.data) == 0:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            if existing.data[0]["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="You don't have permission to update this profile")
            
            # Prepare update data
            update_data = {}
            if name is not None:
                if not name.strip():
                    raise HTTPException(status_code=400, detail="Profile name cannot be empty")
                update_data["name"] = name.strip()
                # Regenerate slug if name changed
                new_slug = ProfileService.generate_slug(name.strip())
                # Ensure uniqueness
                base_slug = new_slug
                counter = 1
                while True:
                    check_result = supabase.table("user_profiles")\
                        .select("id")\
                        .eq("user_id", user_id)\
                        .eq("slug", new_slug)\
                        .neq("id", profile_id)\
                        .execute()
                    
                    if not check_result.data or len(check_result.data) == 0:
                        break
                    
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
                    
                    if counter > 1000:
                        raise HTTPException(status_code=500, detail="Failed to generate unique slug")
                update_data["slug"] = new_slug
            
            if description is not None:
                update_data["description"] = description.strip() if description else None
            
            if not update_data:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            # Update profile
            result = supabase.table("user_profiles")\
                .update(update_data)\
                .eq("id", profile_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=500, detail="Failed to update profile")
            
            profile = result.data[0]
            return UserProfile(
                id=profile["id"],
                name=profile["name"],
                description=profile.get("description"),
                slug=profile["slug"],
                display_order=profile["display_order"],
                created_at=profile["created_at"],
                updated_at=profile["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Update user profile error: {e}")
            raise HTTPException(status_code=500, detail="Failed to update user profile")

    @staticmethod
    async def delete_user_profile(
        profile_id: str,
        user_id: str,
        token: Optional[str] = None
    ) -> MessageResponse:
        """
        Delete a user profile
        
        Args:
            profile_id: The profile ID
            user_id: The user's ID (for authorization)
            token: Optional user token for auth
            
        Returns:
            MessageResponse with success status
        """
        try:
            supabase = get_user_client(token)
            
            # Verify ownership
            existing = supabase.table("user_profiles")\
                .select("user_id")\
                .eq("id", profile_id)\
                .execute()
            
            if not existing.data or len(existing.data) == 0:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            if existing.data[0]["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="You don't have permission to delete this profile")
            
            # Delete all projects assigned to this profile first
            # This ensures projects are deleted before the profile is deleted
            supabase.table("impact_projects")\
                .delete()\
                .eq("profile_id", profile_id)\
                .eq("user_id", user_id)\
                .execute()
            
            # Delete profile
            result = supabase.table("user_profiles")\
                .delete()\
                .eq("id", profile_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return MessageResponse(
                success=True,
                message="Profile and all assigned projects deleted successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Delete user profile error: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete user profile")

    