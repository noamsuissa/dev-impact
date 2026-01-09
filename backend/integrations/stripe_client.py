"""Stripe integration client.
Thin wrapper around Stripe SDK with no business logic.
"""

from datetime import UTC, datetime
from typing import Any

import stripe
from fastapi import HTTPException

from backend.core.config import StripeConfig
from supabase import Client


class StripeClient:
    """Client for Stripe payment operations."""

    def __init__(self, config: StripeConfig):
        """Initialize Stripe client with configuration.

        Args:
        ----
            config: Stripe configuration object

        """
        self.config = config
        # Set Stripe API key
        stripe.api_key = config.secret_key

    def _validate_config(self) -> None:
        """Validate that all required configuration is present.

        Raises
        ------
            HTTPException: If required configuration is missing

        """
        if not self.config.secret_key:
            raise HTTPException(status_code=500, detail="Stripe secret key not configured")
        if not self.config.publishable_key:
            raise HTTPException(status_code=500, detail="Stripe publishable key not configured")

    def _get_price_id(self, billing_period: str) -> str:
        """Get price ID based on billing period.

        Args:
        ----
            billing_period: "monthly" or "yearly"

        Returns:
        -------
            Price ID for the specified billing period

        Raises:
        ------
            HTTPException: If price ID not configured

        """
        price_id = self.config.price_id_yearly if billing_period == "yearly" else self.config.price_id_monthly

        if not price_id:
            raise HTTPException(
                status_code=500,
                detail=f"Stripe price ID not configured for {billing_period} billing",
            )

        return price_id

    async def create_checkout_session(
        self,
        client: Client,
        user_id: str,
        user_email: str,
        success_url: str,
        cancel_url: str,
        billing_period: str = "monthly",
    ) -> dict[str, Any]:
        """Create a Stripe Checkout session for Pro plan subscription.

        Args:
        ----
            client: Supabase client
            user_id: The authenticated user's ID
            user_email: User's email address
            success_url: URL to redirect to after successful payment
            cancel_url: URL to redirect to if user cancels
            billing_period: "monthly" or "yearly" billing period

        Returns:
        -------
            Dictionary with checkout_url and session_id

        Raises:
        ------
            HTTPException: If checkout session creation fails

        """
        try:
            self._validate_config()
            price_id = self._get_price_id(billing_period)

            # Check for existing Stripe customer ID in database
            stripe_customer_id = None
            try:
                profile_response = client.table("profiles").select("stripe_customer_id").eq("id", user_id).single().execute()

                if profile_response.data:
                    stripe_customer_id = profile_response.data.get("stripe_customer_id")
            except Exception as e:
                print(f"Error fetching profile for Stripe customer ID: {e}")
                raise HTTPException(status_code=500, detail="Failed to fetch profile for Stripe customer ID") from e

            # Prepare session arguments
            session_args = {
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "client_reference_id": user_id,
                "metadata": {
                    "user_id": user_id,
                },
                "subscription_data": {
                    "metadata": {
                        "user_id": user_id,
                    }
                },
            }

            # If we have an existing customer ID, use it
            if stripe_customer_id:
                session_args["customer"] = stripe_customer_id
            else:
                session_args["customer_email"] = user_email

            # Create Stripe Checkout Session
            try:
                session = stripe.checkout.Session.create(**session_args)
            except stripe.error.InvalidRequestError as e:
                # If customer doesn't exist (e.g., was deleted), clear it and retry
                if "customer" in session_args and "No such customer" in str(e):
                    print(f"Customer {stripe_customer_id} not found, clearing and retrying: {e}")
                    # Clear customer ID from database
                    try:
                        client.table("profiles").update({"stripe_customer_id": None}).eq("id", user_id).execute()
                    except Exception as db_error:
                        print(f"Error clearing invalid customer ID: {db_error}")
                        raise HTTPException(status_code=500, detail="Failed to clear invalid customer ID") from db_error
                    # Retry without customer ID
                    session_args.pop("customer", None)
                    session_args["customer_email"] = user_email
                    session = stripe.checkout.Session.create(**session_args)
                else:
                    raise

            return {"checkout_url": session.url, "session_id": session.id}

        except stripe.AuthenticationError as e:
            print(f"Stripe authentication error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Payment system configuration error. Please contact support.",
            ) from e
        except stripe.InvalidRequestError as e:
            print(f"Stripe invalid request error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Payment configuration error. Please contact support.",
            ) from e
        except stripe.StripeError as e:
            print(f"Stripe error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Payment system temporarily unavailable. Please try again later.",
            ) from e
        except HTTPException:
            raise
        except Exception as e:
            print(f"Checkout session creation error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Unable to process payment request. Please try again later.",
            ) from e

    async def handle_webhook_event(self, client: Client, payload: bytes, sig_header: str) -> None:
        """Handle Stripe webhook events.

        Args:
        ----
            client: Supabase client
            payload: Raw request body
            sig_header: Stripe signature header

        Raises:
        ------
            HTTPException: For invalid signature or payload

        """
        try:
            if not self.config.webhook_secret:
                print("Warning: STRIPE_WEBHOOK_SECRET not configured")
                return

            try:
                event = stripe.Webhook.construct_event(payload, sig_header, self.config.webhook_secret)
            except ValueError as e:
                raise HTTPException(status_code=400, detail="Invalid payload") from e
            except stripe.SignatureVerificationError as e:
                raise HTTPException(status_code=400, detail="Invalid signature") from e

            # Handle the event
            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                await self._handle_checkout_completed(client, session)
            elif event["type"] in [
                "customer.subscription.updated",
                "customer.subscription.deleted",
                "customer.subscription.created",
            ]:
                subscription = event["data"]["object"]
                await self._handle_subscription_updated(client, subscription)
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error handling webhook event: {e}")
            raise HTTPException(status_code=500, detail="Internal server error") from e

    async def _handle_checkout_completed(self, client: Client, session: dict[str, Any]) -> None:
        """Handle successful checkout session.

        Args:
        ----
            client: Supabase client
            session: Stripe checkout session data

        """
        user_id = session.get("client_reference_id")
        customer_id = session.get("customer")

        if user_id and customer_id:
            await self._update_customer_id(client, user_id, customer_id)
            await self._update_subscription_type(client, user_id, "pro")

    async def _update_customer_id(self, client: Client, user_id: str, customer_id: str) -> None:
        """Update user profile with Stripe Customer ID.

        Args:
        ----
            client: Supabase client
            user_id: User's ID
            customer_id: Stripe customer ID

        """
        try:
            client.table("profiles").update({"stripe_customer_id": customer_id}).eq("id", user_id).execute()

            print(f"Updated Stripe customer ID for user {user_id}")

        except Exception as e:
            print(f"Failed to update Stripe customer ID: {e}")
            raise HTTPException(status_code=500, detail="Failed to update Stripe customer ID") from e

    async def _update_subscription_type(self, client: Client, user_id: str, subscription_type: str) -> None:
        """Update user profile with subscription type.

        Args:
        ----
            client: Supabase client
            user_id: User's ID
            subscription_type: Subscription type

        """
        try:
            client.table("profiles").update({"subscription_type": subscription_type}).eq("id", user_id).execute()

            print(f"Updated subscription type for user {user_id}")

        except Exception as e:
            print(f"Failed to update subscription type: {e}")
            raise HTTPException(status_code=500, detail="Failed to update subscription type") from e

    async def _handle_subscription_updated(self, client: Client, subscription: dict[str, Any]) -> None:
        """Handle subscription updates (created, updated, deleted).

        Args:
        ----
            client: Supabase client
            subscription: Stripe subscription data

        """
        try:
            customer_id = subscription.get("customer")
            status = subscription.get("status")
            cancel_at_period_end = subscription.get("cancel_at_period_end", False)
            current_period_end_ts = subscription.get("current_period_end")

            # Convert timestamp to datetime
            current_period_end = datetime.fromtimestamp(current_period_end_ts, UTC) if current_period_end_ts else None

            # Determine subscription type based on status
            subscription_type = "pro" if status in ["active", "trialing"] else "free"

            # Find user by stripe_customer_id
            response = client.table("profiles").select("id").eq("stripe_customer_id", customer_id).execute()

            if response.data:
                for user in response.data:
                    user_id = user["id"]

                    update_data = {
                        "subscription_type": subscription_type,
                        "subscription_status": status,
                        "cancel_at_period_end": cancel_at_period_end,
                    }
                    if current_period_end:
                        update_data["current_period_end"] = current_period_end.isoformat()

                    client.table("profiles").update(update_data).eq("id", user_id).execute()
                    print(f"Updated subscription status for user {user_id}: {status}")
            else:
                print(f"No user found for Stripe customer {customer_id}")

        except Exception as e:
            print(f"Error handling subscription update: {e}")
            raise HTTPException(status_code=500, detail="Failed to handle subscription update") from e

    async def cancel_subscription(self, client: Client, user_id: str) -> None:
        """Cancel a user's subscription (at period end).

        Args:
        ----
            client: Supabase client
            user_id: The user's ID

        Raises:
        ------
            HTTPException: If cancellation fails

        """
        try:
            self._validate_config()

            # Get customer ID
            profile_response = client.table("profiles").select("stripe_customer_id").eq("id", user_id).single().execute()

            if not profile_response.data or not profile_response.data.get("stripe_customer_id"):
                raise HTTPException(status_code=400, detail="No subscription found")

            stripe_customer_id = profile_response.data.get("stripe_customer_id")

            # List subscriptions
            subscriptions = stripe.Subscription.list(customer=stripe_customer_id, status="active", limit=1)

            if not subscriptions.data:
                raise HTTPException(status_code=400, detail="No active subscription found")

            subscription_id = subscriptions.data[0].id

            # Update subscription to cancel at period end
            updated_subscription = stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)

            # Immediately update database with the returned info
            current_period_end_ts = updated_subscription.get("current_period_end")
            current_period_end = datetime.fromtimestamp(current_period_end_ts, UTC) if current_period_end_ts else None

            client.table("profiles").update(
                {
                    "cancel_at_period_end": True,
                    "current_period_end": (current_period_end.isoformat() if current_period_end else None),
                    "subscription_status": updated_subscription.get("status"),
                }
            ).eq("id", user_id).execute()

            print(f"Cancelled subscription for user {user_id}. Access until {current_period_end}")

        except HTTPException:
            raise
        except stripe.StripeError as e:
            print(f"Stripe error canceling subscription: {e}")
            raise HTTPException(status_code=500, detail="Failed to cancel subscription") from e
        except Exception as e:
            print(f"Error canceling subscription: {e}")
            raise HTTPException(status_code=500, detail="Internal server error") from e

    async def get_subscription_info(self, client: Client, user_id: str) -> dict[str, Any]:
        """Get subscription information for a user.

        Args:
        ----
            client: Supabase client
            user_id: The user's ID

        Returns:
        -------
            Dictionary with subscription information

        """
        try:
            # Get user profile with subscription info
            profile_response = (
                client.table("profiles")
                .select("subscription_type, subscription_status, cancel_at_period_end, current_period_end, stripe_customer_id")
                .eq("id", user_id)
                .single()
                .execute()
            )

            if not profile_response.data:
                raise HTTPException(status_code=404, detail="Profile not found")

            profile_data = profile_response.data

            return {
                "subscription_type": profile_data.get("subscription_type", "free"),
                "subscription_status": profile_data.get("subscription_status"),
                "cancel_at_period_end": profile_data.get("cancel_at_period_end", False),
                "current_period_end": profile_data.get("current_period_end"),
                "has_stripe_customer": bool(profile_data.get("stripe_customer_id")),
            }

        except HTTPException:
            raise
        except Exception as e:
            print(f"Error getting subscription info: {e}")
            raise HTTPException(status_code=500, detail="Internal server error") from e
