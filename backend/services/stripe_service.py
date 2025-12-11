"""
Stripe Service - Handle Stripe payment operations
"""
import os
import stripe
from typing import Dict, Any
from fastapi import HTTPException
from utils import auth_utils

class StripeService:
    """Service for handling Stripe operations"""
    
    @staticmethod
    def _get_stripe_config() -> Dict[str, str]:
        """
        Get Stripe configuration from environment variables
        
        Returns:
            Dictionary with Stripe API keys and price ID
            
        Raises:
            HTTPException if required environment variables are missing
        """
        secret_key = os.getenv("STRIPE_SECRET_KEY")
        publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        price_id = os.getenv("STRIPE_PRICE_ID")
        
        if not secret_key:
            raise HTTPException(
                status_code=500,
                detail="Stripe secret key not configured"
            )
        
        if not price_id:
            raise HTTPException(
                status_code=500,
                detail="Stripe price ID not configured"
            )
        
        return {
            "secret_key": secret_key,
            "publishable_key": publishable_key,
            "price_id": price_id
        }
    
    @staticmethod
    async def create_checkout_session(
        user_id: str,
        user_email: str,
        success_url: str,
        cancel_url: str,
        auth_token: str
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session for Pro plan subscription
        
        Args:
            user_id: The authenticated user's ID
            user_email: User's email address
            success_url: URL to redirect to after successful payment
            cancel_url: URL to redirect to if user cancels
            auth_token: Authorization token for Supabase client
            
        Returns:


            Dictionary with checkout_url and session_id
            
        Raises:
            HTTPException if checkout session creation fails
        """
        try:
            config = StripeService._get_stripe_config()
            stripe.api_key = config["secret_key"]
            
            # Check for existing Stripe customer ID in database
            stripe_customer_id = None
            try:
                supabase = auth_utils.get_supabase_client(auth_token)
                profile_response = supabase.table("profiles") \
                    .select("stripe_customer_id") \
                    .eq("id", user_id) \
                    .single() \
                    .execute()
                
                if profile_response.data:
                    stripe_customer_id = profile_response.data.get("stripe_customer_id")
            except Exception as e:
                print(f"Error fetching profile for Stripe customer ID: {e}")
                # Proceed without it, Stripe will create a new one
            
            # Prepare session arguments
            session_args = {
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": config["price_id"],
                        "quantity": 1,
                    }
                ],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "client_reference_id": user_id,  # Link to our user
                "metadata": {
                    "user_id": user_id,
                },
                "subscription_data": {
                    "metadata": {
                        "user_id": user_id,
                    }
                }
            }
            
            # If we have an existing customer ID, use it
            if stripe_customer_id:
                session_args["customer"] = stripe_customer_id
                # When customer is provided, customer_email is not allowed/needed
            else:
                # Otherwise, prefill email for new customer creation
                session_args["customer_email"] = user_email
                
            # Create Stripe Checkout Session
            session = stripe.checkout.Session.create(**session_args)

            
            return {
                "checkout_url": session.url,
                "session_id": session.id
            }
            
        except stripe.error.AuthenticationError as e:
            # Invalid API key
            print(f"Stripe authentication error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Payment system configuration error. Please contact support."
            )
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters (e.g., wrong price ID)
            print(f"Stripe invalid request error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Payment configuration error. Please contact support."
            )
        except stripe.error.StripeError as e:
            # Other Stripe errors
            print(f"Stripe error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Payment system temporarily unavailable. Please try again later."
            )
        except HTTPException:
            # Re-raise our own HTTPExceptions (from config validation)
            raise
        except Exception as e:
            print(f"Checkout session creation error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Unable to process payment request. Please try again later."
            )

    @staticmethod
    async def handle_webhook_event(payload: bytes, sig_header: str) -> None:
        """
        Handle Stripe webhook events
        
        Args:
            payload: Raw request body
            sig_header: Stripe signature header
            
        Raises:
            HTTPException for invalid signature or payload
        """
        try:
            webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
            if not webhook_secret:
                print("Warning: STRIPE_WEBHOOK_SECRET not configured")
                return

            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except ValueError as e:
                # Invalid payload
                raise HTTPException(status_code=400, detail="Invalid payload")
            except stripe.error.SignatureVerificationError as e:
                # Invalid signature
                raise HTTPException(status_code=400, detail="Invalid signature")

            # Handle the event
            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                await StripeService._handle_checkout_completed(session)
        except HTTPException:
            # Re-raise our own HTTPExceptions (from config validation)
            raise
        except Exception as e:
            print(f"Error handling webhook event: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @staticmethod
    async def _handle_checkout_completed(session: Dict[str, Any]) -> None:
        """
        Handle successful checkout session
        
        Extracts user ID and customer ID to update the profile.
        """
        user_id = session.get("client_reference_id")
        customer_id = session.get("customer")
        
        if user_id and customer_id:
            await StripeService._update_customer_id(user_id, customer_id)
            await StripeService._update_subscription_type(user_id, "pro")

    @staticmethod
    async def _update_customer_id(user_id: str, customer_id: str) -> None:
        """
        Update user profile with Stripe Customer ID
        """
        try:
            # Get admin client (uses Service Role Key from env)
            supabase = auth_utils.get_supabase_client()
            
            supabase.table("profiles").update({
                "stripe_customer_id": customer_id
            }).eq("id", user_id).execute()
            
            print(f"Updated Stripe customer ID for user {user_id}")
            
        except Exception as e:
            print(f"Failed to update Stripe customer ID: {e}")
            # Don't raise here to avoid failing the webhook response to Stripe

    @staticmethod
    async def _update_subscription_type(user_id: str, subscription_type: str) -> None:
        """
        Update user profile with subscription type
        """
        try:
            # Get admin client (uses Service Role Key from env)
            supabase = auth_utils.get_supabase_client()
            
            supabase.table("profiles").update({
                "subscription_type": subscription_type
            }).eq("id", user_id).execute()
            
            print(f"Updated subscription type for user {user_id}")
            
        except Exception as e:
            print(f"Failed to update subscription type: {e}")
            # Don't raise here to avoid failing the webhook response to Stripe


