"""
User Service - Handle user profile operations with Supabase
"""
import re
from typing import Dict, Any
from fastapi import HTTPException
from backend.schemas.user import UserProfile, CheckUsernameResponse
from backend.schemas.auth import MessageResponse
from backend.services.stripe_service import StripeService
from backend.utils.dependencies import ServiceDBClient

class UserService:
    """Service for handling user profile operations."""

    @staticmethod
    async def get_profile(client: ServiceDBClient, user_id: str | None = None) -> UserProfile:
        """
        Get user profile by ID
        
        Args:
            client: Supabase client (injected from router)
            user_id: User's ID
            
        Returns:
            UserProfile containing user profile data
        """

        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        try:
            result = client.table("profiles")\
                .select("*")\
                .eq("id", user_id)\
                .maybe_single()\
                .execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            return UserProfile(
                id=result.data["id"],
                username=result.data["username"],
                full_name=result.data["full_name"],
                github_username=result.data["github_username"],
                github_avatar_url=result.data["github_avatar_url"],
                city=result.data.get("city"),
                country=result.data.get("country"),
                is_published=result.data["is_published"],
                created_at=result.data["created_at"],
                updated_at=result.data["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            # Check if it's a "not found" type error from Supabase
            error_str = str(e).lower()
            if "not found" in error_str or "no rows" in error_str or "pgrst" in error_str:
                raise HTTPException(status_code=404, detail="Profile not found")
            print(f"Get profile error: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch profile")

    @staticmethod
    async def update_profile(client: ServiceDBClient, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Update user profile
        
        Args:
            client: Supabase client (injected from router)
            user_id: User's ID
            profile_data: Profile data to update
            
        Returns:
            UserProfile containing updated profile data
        """
        try:
            
            # Prepare update data
            # Include all values, even None, to allow clearing fields (e.g., disconnecting GitHub)
            # Only exclude keys that weren't provided in the request
            update_data = {k: v for k, v in profile_data.items()}
            
            if not update_data:
                # If no data to update, just return current profile
                return await UserService.get_profile(client, user_id)
            
            result = client.table("profiles")\
                .update(update_data)\
                .eq("id", user_id)\
                .execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            # Update returns a list, get the first item
            updated_profile = result.data[0]
            
            return UserProfile(
                id=updated_profile["id"],
                username=updated_profile["username"],
                full_name=updated_profile["full_name"],
                github_username=updated_profile["github_username"],
                github_avatar_url=updated_profile["github_avatar_url"],
                city=updated_profile.get("city"),
                country=updated_profile.get("country"),
                is_published=updated_profile["is_published"],
                created_at=updated_profile["created_at"],
                updated_at=updated_profile["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Update profile error: {e}")
            raise HTTPException(status_code=500, detail="Failed to update profile")

    @staticmethod
    async def create_or_update_profile(client: ServiceDBClient, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Create or update user profile (for onboarding)
        
        Args:
            client: Supabase client (injected from router)
            user_id: User's ID
            profile_data: Profile data
            
        Returns:
            UserProfile containing profile data
        """
        try:
            
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
            
            result = client.table("profiles")\
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
                city=result.data.get("city"),
                country=result.data.get("country"),
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
    async def delete_account(
        client: ServiceDBClient,
        user_id: str,
        stripe_service: type[StripeService]
    ) -> MessageResponse:
        """
        Delete user account (profile and auth user)
        
        Args:
            client: Supabase client (injected from router)
            user_id: User's ID
            stripe_service: Stripe service class (injected from router)
            
        Returns:
            MessageResponse with success message
        """
        try:
            # 1. Try to cancel subscription if exists
            try:
                await stripe_service.cancel_subscription(client, user_id)
            except Exception as e:
                # Log but continue - user might not have a subscription
                print(f"Subscription cancellation check during account delete: {e}")
            
            # 2. Delete profile (this will cascade delete related data if FK constraints are set)
            client.table("profiles")\
                .delete()\
                .eq("id", user_id)\
                .execute()
            
            # 3. Delete auth user using Admin API
            client.auth.admin.delete_user(user_id)
            
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
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        # Lowercase alphanumeric and hyphens only, 3-50 characters
        pattern = r'^[a-z0-9-]{3,50}$'
        return bool(re.match(pattern, username))

    @staticmethod
    async def check_username(client: ServiceDBClient, username: str) -> CheckUsernameResponse:
        """
        Check if a username is available for publishing portfolios
        
        Args:
            client: Supabase client (injected from router)
            username: The username to check
            
        Returns:
            CheckUsernameResponse with availability status
        """
        try:
            if not UserService.validate_username(username):
                return CheckUsernameResponse(
                    available=False,
                    valid=False,
                    message="Username must be 3-50 characters, lowercase letters, numbers, and hyphens only"
                )
            
            # Use RPC call to check availability (checks format, reserved names, and existing profiles)
            result = client.rpc("is_username_available", {"desired_username": username}).execute()
            
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
