"""
User Service - Handle user profile operations with Supabase
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
from ..utils.auth_utils import get_supabase_client
from ..schemas.user import UserProfile, SubscriptionInfoResponse
from ..schemas.auth import MessageResponse
from .stripe_service import StripeService

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
            supabase = get_supabase_client()
            
            # Delete profile (this will cascade delete related data if FK constraints are set)
            supabase.table("profiles")\
                .delete()\
                .eq("id", user_id)\
                .execute()
            
            # Delete auth user using Admin API
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

    @staticmethod
    async def get_subscription_info(
        user_id: str,
        token: Optional[str] = None
    ) -> SubscriptionInfoResponse:
        """
        Get user's subscription information and profile limits
        
        Args:
            user_id: The user's ID
            token: Optional user token for auth
            
        Returns:
            SubscriptionInfoResponse with subscription_type, profile_count, max_profiles, can_add_profile
        """
        try:
            supabase = get_supabase_client(access_token=token)
            
            # Get user's subscription type from profiles table
            profile_result = supabase.table("profiles")\
                .select("subscription_type, subscription_status, cancel_at_period_end, current_period_end")\
                .eq("id", user_id)\
                .single()\
                .execute()
            
            data = profile_result.data or {}
            subscription_type = data.get("subscription_type", "free")
            
            # Count existing profiles
            count_result = supabase.table("user_profiles")\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .execute()
            
            profile_count = len(count_result.data) if count_result.data else 0
            
            # Set max profiles based on subscription
            if subscription_type == "pro":
                max_profiles = 1000  # Unlimited for pro
            else:
                max_profiles = 3  # Free users limited to 3
            
            return SubscriptionInfoResponse(
                subscription_type=subscription_type,
                subscription_status=data.get("subscription_status"),
                cancel_at_period_end=data.get("cancel_at_period_end", False),
                current_period_end=data.get("current_period_end"),
                profile_count=profile_count,
                max_profiles=max_profiles,
                can_add_profile=profile_count < max_profiles
            )
        except Exception as e:
            print(f"Get subscription info error: {e}")
            raise HTTPException(status_code=500, detail="Failed to get subscription info")

    @staticmethod
    async def cancel_subscription(user_id: str) -> MessageResponse:
        """
        Cancel user's subscription
        
        Args:
            user_id: The user's ID
            
        Returns:
            MessageResponse indicating success
        """
        try:
            await StripeService.cancel_subscription(user_id)
            return MessageResponse(
                success=True,
                message="Subscription has been scheduled for cancellation at the end of the billing period"
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error cancelling subscription: {e}")
            raise HTTPException(status_code=500, detail="Failed to cancel subscription")
