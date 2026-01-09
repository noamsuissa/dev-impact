"""Protocol definitions for services and integrations.
Enables interface-based programming and easier testing with mocks.
"""

from typing import Any, Protocol

from supabase import Client


# Integration Client Protocols
class IStripeClient(Protocol):
    """Interface for Stripe payment operations"""

    async def create_checkout_session(
        self,
        client: Client,
        user_id: str,
        success_url: str,
        cancel_url: str,
        billing_period: str,
    ) -> dict[str, Any]:
        """Create a Stripe checkout session."""

    async def cancel_subscription(self, client: Client, user_id: str) -> None:
        """Cancel a user's Stripe subscription."""

    async def handle_webhook_event(self, client: Client, payload: bytes, signature: str) -> dict[str, Any]:
        """Handle and process a Stripe webhook event."""

    async def get_subscription_info(self, client: Client, user_id: str) -> dict[str, Any]:
        """Get subscription information for a user."""


class IEmailClient(Protocol):
    """Interface for email operations"""

    async def send_email(self, to_email: str, subject: str, template_name: str, context: dict[str, Any]) -> None:
        """Send an email using a template."""


class IGitHubClient(Protocol):
    """Interface for GitHub API operations"""

    async def initiate_device_flow(self) -> dict[str, Any]:
        """Initiate GitHub OAuth device flow."""

    async def poll_for_token(self, device_code: str) -> str | None:
        """Poll for OAuth token from device code."""

    async def get_user_profile(self, access_token: str) -> dict[str, Any]:
        """Get GitHub user profile information."""


class ILLMClient(Protocol):
    """Interface for LLM operations"""

    async def generate_completion(self, messages: list[dict[str, str]], model: str | None = None) -> str:
        """Generate LLM completion from messages."""

    def get_available_models(self) -> list[dict[str, str]]:
        """Get list of available LLM models."""


# Business Service Protocols
class IUserService(Protocol):
    """Interface for user business logic"""

    async def get_profile(self, client: Client, user_id: str) -> dict[str, Any]:
        """Get user profile."""

    async def update_profile(self, client: Client, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update user profile."""

    async def create_or_update_profile(self, client: Client, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create or update user profile."""

    async def check_username(self, client: Client, username: str) -> dict[str, Any]:
        """Check if username is available."""

    async def delete_account(self, client: Client, user_id: str) -> dict[str, Any]:
        """Delete user account."""


class ISubscriptionService(Protocol):
    """Interface for subscription business logic"""

    async def get_subscription_info(self, client: Client, user_id: str) -> dict[str, Any]:
        """Get subscription information."""

    async def cancel_subscription(self, client: Client, user_id: str) -> dict[str, Any]:
        """Cancel user subscription."""


class IWaitlistService(Protocol):
    """Interface for waitlist business logic"""

    async def signup(self, client: Client, email: str, name: str | None) -> dict[str, Any]:
        """Sign up for waitlist."""


class IPortfolioService(Protocol):
    """Interface for portfolio business logic"""

    async def create_portfolio(
        self,
        client: Client,
        subscription_info: dict[str, Any],
        user_id: str,
        name: str,
        description: str | None,
    ) -> dict[str, Any]:
        """Create a new portfolio."""

    async def list_portfolios(self, client: Client, user_id: str) -> list[dict[str, Any]]:
        """List user's portfolios."""

    async def get_portfolio(self, client: Client, portfolio_id: str, user_id: str) -> dict[str, Any]:
        """Get a specific portfolio."""


class IProjectService(Protocol):
    """Interface for project business logic"""

    async def create_project(self, client: Client, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new project."""

    async def list_projects(self, client: Client, user_id: str, portfolio_id: str | None) -> list[dict[str, Any]]:
        """List user's projects."""


class IAuthService(Protocol):
    """Interface for authentication business logic"""

    async def sign_up(self, client: Client, email: str, password: str) -> dict[str, Any]:
        """Sign up a new user."""

    async def sign_in(self, client: Client, email: str, password: str) -> dict[str, Any]:
        """Sign in a user."""


class IMFAService(Protocol):
    """Interface for MFA business logic"""

    async def mfa_enroll(self, client: Client, user_id: str) -> dict[str, Any]:
        """Enroll user in MFA."""

    async def mfa_verify(self, client: Client, user_id: str, code: str) -> dict[str, Any]:
        """Verify MFA code."""
