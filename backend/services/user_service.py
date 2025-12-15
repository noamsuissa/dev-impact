"""
User Service - Handle user profile operations with Supabase
"""
from typing import Dict, Any
from fastapi import HTTPException
from backend.utils.auth_utils import get_supabase_client
from backend.schemas.user import UserProfile
from backend.schemas.auth import MessageResponse
from backend.services.stripe_service import StripeService

class UserService:
    """Service for handling user profile operations."""

    @staticmethod
    async def get_profile(user_id: str) -> UserProfile:
        """
        Get user profile by ID
        
        Args:
            user_id: User's ID
            
        Returns:
            UserProfile containing user profile data
        """
        try:
            supabase = get_supabase_client()
            
            result = supabase.table("profiles")\
                .select("*")\
                .eq("id", user_id)\
                .single()\
                .execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            return UserProfile(
                id=result.data["id"],
                username=result.data["username"],
                full_name=result.data["full_name"],
                github_username=result.data["github_username"],
                github_avatar_url=result.data["github_avatar_url"],
                is_published=result.data["is_published"],
                created_at=result.data["created_at"],
                updated_at=result.data["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get profile error: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch profile")

    @staticmethod
    async def update_profile(user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Update user profile
        
        Args:
            user_id: User's ID
            profile_data: Profile data to update
            
        Returns:
            UserProfile containing updated profile data
        """
        try:
            supabase = get_supabase_client()
            
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
                raise HTTPException(status_code=404, detail="Profile not found")
            
            return UserProfile(
                id=result.data["id"],
                username=result.data["username"],
                full_name=result.data["full_name"],
                github_username=result.data["github_username"],
                github_avatar_url=result.data["github_avatar_url"],
                is_published=result.data["is_published"],
                created_at=result.data["created_at"],
                updated_at=result.data["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Update profile error: {e}")
            raise HTTPException(status_code=500, detail="Failed to update profile")

    @staticmethod
    async def create_or_update_profile(user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Create or update user profile (for onboarding)
        
        Args:
            user_id: User's ID
            profile_data: Profile data
            
        Returns:
            UserProfile containing profile data
        """
        try:
            supabase = get_supabase_client()
            
            # Prepare upsert data
            upsert_data = {
                "id": user_id,
                **profile_data
            }
            
            # Generate username if not provided
            if "username" not in upsert_data and "full_name" in profile_data:
                username = profile_data["full_name"].lower().replace(" ", "")
                # Remove special characters
                username = "".join(c for c in username if c.isalnum() or c == "-")
                upsert_data["username"] = username
            
            result = supabase.table("profiles")\
                .upsert(upsert_data)\
                .execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create/update profile")
            
            return UserProfile(
                id=result.data["id"],
                username=result.data["username"],
                full_name=result.data["full_name"],
                github_username=result.data["github_username"],
                github_avatar_url=result.data["github_avatar_url"],
                is_published=result.data["is_published"],
                created_at=result.data["created_at"],
                updated_at=result.data["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Create/update profile error: {e}")
            raise HTTPException(status_code=500, detail="Failed to create/update profile")

    @staticmethod
    async def delete_account(user_id: str) -> MessageResponse:
        """
        Delete user account (profile and auth user)
        
        Args:
            user_id: User's ID
            
        Returns:
            MessageResponse with success message
        """
        try:
            # 1. Try to cancel subscription if exists
            try:
                await StripeService.cancel_subscription(user_id)
            except Exception as e:
                # Log but continue - user might not have a subscription
                print(f"Subscription cancellation check during account delete: {e}")

            supabase = get_supabase_client()
            
            # 2. Delete profile (this will cascade delete related data if FK constraints are set)
            supabase.table("profiles")\
                .delete()\
                .eq("id", user_id)\
                .execute()
            
            # 3. Delete auth user using Admin API
            supabase.auth.admin.delete_user(user_id)
            
            return MessageResponse(
                success=True,
                message="Account deleted successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Delete account error: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete account")
