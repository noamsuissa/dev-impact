"""
Waitlist Service - Handle waitlist operations
"""

from typing import Optional
from fastapi import HTTPException
from supabase import Client
import logging

from backend.schemas.waitlist import WaitlistEntry, WaitlistResponse
from backend.integrations.email_client import EmailClient

logger = logging.getLogger(__name__)


class WaitlistService:
    """Service for handling waitlist operations."""

    def __init__(self, email_client: EmailClient):
        """
        Initialize WaitlistService with dependencies.

        Args:
            email_client: Email integration client for sending emails
        """
        self.email_client = email_client

    async def signup(
        self, client: Client, email: str, name: Optional[str] = None
    ) -> WaitlistResponse:
        """
        Add a user to the waitlist and send confirmation email.

        Args:
            client: Supabase client
            email: User's email address
            name: Optional user's name

        Returns:
            WaitlistResponse with success status and entry data
        """
        try:
            # Check if email already exists
            existing = (
                client.table("waitlist")
                .select("*")
                .eq("email", email.lower().strip())
                .execute()
            )

            if existing.data:
                # Email already exists, return existing entry
                entry_data = existing.data[0]
                return WaitlistResponse(
                    success=True,
                    message="You're already on the waitlist!",
                    entry=WaitlistEntry(**entry_data),
                )

            # Insert new waitlist entry
            entry_data = {
                "email": email.lower().strip(),
                "name": name.strip() if name and name.strip() else None,
            }

            result = client.table("waitlist").insert(entry_data).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to add to waitlist")

            entry = WaitlistEntry(**result.data[0])

            # Send confirmation email
            email_sent = await self.email_client.send_email(
                to_email=email,
                subject="Welcome to the Dev Impact Waitlist!",
                template_name="waitlist_confirmation.html",
                template_vars={"name": name or "there", "email": email},
            )

            if not email_sent:
                logger.warning(
                    f"Failed to send confirmation email to {email}, but user was added to waitlist"
                )

            return WaitlistResponse(
                success=True,
                message="Successfully added to waitlist! Check your email for confirmation.",
                entry=entry,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Waitlist signup error: {e}")
            raise HTTPException(status_code=500, detail="Failed to add to waitlist")
