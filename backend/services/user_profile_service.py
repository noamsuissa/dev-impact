"""
User Profile Service - Handle user profile operations with Supabase
"""
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from services.profile_service import ProfileService

class UserProfileService:
    """Service for handling user profile operations with Supabase."""

    @staticmethod
    async def create_user_profile(
        user_id: str,
        name: str,
        description: Optional[str] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new user profile
        
        Args:
            user_id: The authenticated user's ID
            name: Profile name
            description: Optional profile description
            token: Optional user token for auth
            
        Returns:
            Dict containing created profile data
        """
        if not name or not name.strip():
            raise HTTPException(
                status_code=400,
                detail="Profile name is required"
            )
        
        supabase = ProfileService.get_supabase_client(user_token=token)
        
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
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate unique slug"
                )
        
        # Get current profile count for display_order
        count_result = supabase.table("user_profiles")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()
        
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
            raise HTTPException(
                status_code=500,
                detail="Failed to create profile"
            )
        
        profile = result.data[0]
        return {
            "id": profile["id"],
            "name": profile["name"],
            "description": profile.get("description"),
            "slug": profile["slug"],
            "display_order": profile["display_order"],
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"]
        }

    @staticmethod
    async def list_user_profiles(
        user_id: str,
        token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all profiles for a user
        
        Args:
            user_id: The user's ID
            token: Optional user token for auth
            
        Returns:
            List of profile dictionaries
        """
        supabase = ProfileService.get_supabase_client(user_token=token)
        
        result = supabase.table("user_profiles")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("display_order")\
            .order("created_at")\
            .execute()
        
        profiles = []
        for profile in result.data:
            profiles.append({
                "id": profile["id"],
                "name": profile["name"],
                "description": profile.get("description"),
                "slug": profile["slug"],
                "display_order": profile["display_order"],
                "created_at": profile["created_at"],
                "updated_at": profile["updated_at"]
            })
        
        return profiles

    @staticmethod
    async def get_user_profile(
        profile_id: str,
        user_id: str,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a single user profile
        
        Args:
            profile_id: The profile ID
            user_id: The user's ID (for authorization)
            token: Optional user token for auth
            
        Returns:
            Profile dictionary
        """
        supabase = ProfileService.get_supabase_client(user_token=token)
        
        result = supabase.table("user_profiles")\
            .select("*")\
            .eq("id", profile_id)\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        
        profile = result.data
        return {
            "id": profile["id"],
            "name": profile["name"],
            "description": profile.get("description"),
            "slug": profile["slug"],
            "display_order": profile["display_order"],
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"]
        }

    @staticmethod
    async def update_user_profile(
        profile_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a user profile
        
        Args:
            profile_id: The profile ID
            user_id: The user's ID (for authorization)
            name: Optional new name
            description: Optional new description
            token: Optional user token for auth
            
        Returns:
            Updated profile dictionary
        """
        supabase = ProfileService.get_supabase_client(user_token=token)
        
        # Verify ownership
        existing = supabase.table("user_profiles")\
            .select("user_id, slug")\
            .eq("id", profile_id)\
            .execute()
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        
        if existing.data[0]["user_id"] != user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to update this profile"
            )
        
        # Prepare update data
        update_data = {}
        if name is not None:
            if not name.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Profile name cannot be empty"
                )
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
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to generate unique slug"
                    )
            update_data["slug"] = new_slug
        
        if description is not None:
            update_data["description"] = description.strip() if description else None
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields to update"
            )
        
        # Update profile
        result = supabase.table("user_profiles")\
            .update(update_data)\
            .eq("id", profile_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=500,
                detail="Failed to update profile"
            )
        
        profile = result.data[0]
        return {
            "id": profile["id"],
            "name": profile["name"],
            "description": profile.get("description"),
            "slug": profile["slug"],
            "display_order": profile["display_order"],
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"]
        }

    @staticmethod
    async def delete_user_profile(
        profile_id: str,
        user_id: str,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a user profile
        
        Args:
            profile_id: The profile ID
            user_id: The user's ID (for authorization)
            token: Optional user token for auth
            
        Returns:
            Success message
        """
        supabase = ProfileService.get_supabase_client(user_token=token)
        
        # Verify ownership
        existing = supabase.table("user_profiles")\
            .select("user_id")\
            .eq("id", profile_id)\
            .execute()
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        
        if existing.data[0]["user_id"] != user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this profile"
            )
        
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
        
        return {
            "success": True,
            "message": "Profile and all assigned projects deleted successfully"
        }

