"""
Subscription Service - Handle subscription operations
"""
from typing import Optional
from fastapi import HTTPException
from backend.schemas.subscription import SubscriptionInfoResponse
from backend.db.client import get_user_client
from backend.schemas.auth import MessageResponse
from backend.services.stripe_service import StripeService

class SubscriptionService:
    """Service for handling subscription operations."""
    
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
            supabase = get_user_client(token)
            
            # Get user's subscription type from profiles table
            profile_result = supabase.table("profiles")\
                .select("subscription_type, subscription_status, cancel_at_period_end, current_period_end")\
                .eq("id", user_id)\
                .single()\
                .execute()
            
            data = profile_result.data or {}
            subscription_type = data.get("subscription_type", "free")
            
            # Count existing profiles
            count_result = (supabase.table("user_profiles")
                .select("id", count="exact") # type: ignore[arg-type]
                .eq("user_id", user_id)
                .execute())
            
            profile_count = len(count_result.data) if count_result.data else 0
            
            # Set max profiles based on subscription
            if subscription_type == "pro":
                max_profiles = 1000  # Unlimited for pro
            else:
                max_profiles = 3  # Free users limited to 3
            
            return SubscriptionInfoResponse(
                subscription_type=subscription_type,
                subscription_status=data.get("subscription_status"),
                cancel_at_period_end=data.get("cancel_at_period_end", False) if data.get("cancel_at_period_end") is not None else False,
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
