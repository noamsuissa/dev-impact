"""
User Service - Handle user profile operations with Supabase
"""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from fastapi import HTTPException
from supabase import create_client, Client

# Load environment variables
load_dotenv()


class UserService:
    """Service for handling user profile operations."""

    @staticmethod
    def get_supabase_client() -> Client:
        """Get Supabase client from environment"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise HTTPException(
                status_code=500,
                detail="Supabase configuration not found"
            )
        
        return create_client(url, key)

    @staticmethod
    async def get_profile(user_id: str) -> Dict[str, Any]:
        """
        Get user profile by ID
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict containing user profile data
        """
        try:
            supabase = UserService.get_supabase_client()
            
            result = supabase.table("profiles")\
                .select("*")\
                .eq("id", user_id)\
                .single()\
                .execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=404,
                    detail="Profile not found"
                )
            
            return result.data
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get profile error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch profile"
            )

    @staticmethod
    async def update_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile
        
        Args:
            user_id: User's ID
            profile_data: Profile data to update
            
        Returns:
            Dict containing updated profile data
        """
        try:
            supabase = UserService.get_supabase_client()
            
            # Prepare update data (only include non-None values)
            update_data = {k: v for k, v in profile_data.items() if v is not None}
            
            if not update_data:
                # If no data to update, just return current profile
                return await UserService.get_profile(user_id)
            
            result = supabase.table("profiles")\
                .update(update_data)\
                .eq("id", user_id)\
                .execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=404,
                    detail="Profile not found"
                )
            
            return result.data[0]
        except HTTPException:
            raise
        except Exception as e:
            print(f"Update profile error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update profile"
            )

    @staticmethod
    async def create_or_update_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update user profile (for onboarding)
        
        Args:
            user_id: User's ID
            profile_data: Profile data
            
        Returns:
            Dict containing profile data
        """
        try:
            supabase = UserService.get_supabase_client()
            
            # Prepare upsert data
            upsert_data = {
                "id": user_id,
                **profile_data
            }
            
            # Generate username if not provided
            if "username" not in upsert_data and "full_name" in profile_data:
                username = profile_data["full_name"].lower().replace(" ", "-")
                # Remove special characters
                username = "".join(c for c in username if c.isalnum() or c == "-")
                upsert_data["username"] = username
            
            result = supabase.table("profiles")\
                .upsert(upsert_data)\
                .execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create/update profile"
                )
            
            return result.data[0]
        except HTTPException:
            raise
        except Exception as e:
            print(f"Create/update profile error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create/update profile"
            )

