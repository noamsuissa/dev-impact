"""Subscription Service - Handle subscription operations"""

from fastapi import HTTPException

from backend.integrations.stripe_client import StripeClient
from backend.schemas.auth import MessageResponse
from backend.schemas.subscription import SubscriptionInfoResponse
from supabase import Client


class SubscriptionService:
    """Service for handling subscription operations."""

    def __init__(self, stripe_client: StripeClient):
        """Initialize SubscriptionService with dependencies.

        Args:
        ----
            stripe_client: Stripe integration client for subscription operations

        """
        self.stripe_client = stripe_client

    async def get_subscription_info(self, client: Client, user_id: str) -> SubscriptionInfoResponse:
        """Get user's subscription information and portfolio limits

        Args:
        ----
            client: Supabase client (injected from router)
            user_id: The user's ID

        Returns:
        -------
            SubscriptionInfoResponse with subscription_type, portfolio_count, max_portfolios, can_add_portfolio

        """
        try:
            # Get user's subscription type from profiles table
            profile_result = (
                client.table("profiles")
                .select("subscription_type, subscription_status, cancel_at_period_end, current_period_end")
                .eq("id", user_id)
                .single()
                .execute()
            )

            data = profile_result.data or {}
            subscription_type = data.get("subscription_type", "free")

            # Count existing portfolios
            portfolio_count_result = client.table("portfolios").select("id", count="exact").eq("user_id", user_id).execute()

            portfolio_count = len(portfolio_count_result.data) if portfolio_count_result.data else 0

            # Count existing projects
            project_count_result = client.table("impact_projects").select("id", count="exact").eq("user_id", user_id).execute()

            project_count = len(project_count_result.data) if project_count_result.data else 0

            # Set max portfolios based on subscription
            if subscription_type == "pro":
                max_portfolios = 1000  # Unlimited for pro
            else:
                max_portfolios = 1  # Free users limited to 1

            # Set max projects based on subscription
            if subscription_type == "pro":
                max_projects = 1000  # Unlimited for pro
            else:
                max_projects = 10  # Free/hobby users limited to 10

            return SubscriptionInfoResponse(
                subscription_type=subscription_type,
                subscription_status=data.get("subscription_status"),
                cancel_at_period_end=(data.get("cancel_at_period_end", False) if data.get("cancel_at_period_end") is not None else False),
                current_period_end=data.get("current_period_end"),
                portfolio_count=portfolio_count,
                max_portfolios=max_portfolios,
                can_add_portfolio=portfolio_count < max_portfolios,
                project_count=project_count,
                max_projects=max_projects,
                can_add_project=project_count < max_projects,
            )
        except Exception as e:
            print(f"Get subscription info error: {e}")
            raise HTTPException(status_code=500, detail="Failed to get subscription info") from e

    async def cancel_subscription(self, client: Client, user_id: str) -> MessageResponse:
        """Cancel user's subscription.

        Args:
        ----
            client: Supabase client
            user_id: The user's ID

        Returns:
        -------
            MessageResponse indicating success

        """
        try:
            await self.stripe_client.cancel_subscription(client, user_id)
            return MessageResponse(
                success=True,
                message="Subscription has been scheduled for cancellation at the end of the billing period",
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error cancelling subscription: {e}")
            raise HTTPException(status_code=500, detail="Failed to cancel subscription") from e
