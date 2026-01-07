"""
Dependency Injection container for FastAPI.
Centralizes all dependency providers and configuration.
"""
from typing import Annotated
from fastapi import Depends
from supabase import Client

from backend.db import client as db_client
from backend.core.config import StripeConfig, EmailConfig, GitHubConfig, LLMConfig
from backend.integrations.stripe_client import StripeClient
from backend.integrations.email_client import EmailClient
from backend.integrations.github_client import GitHubClient
from backend.integrations.llm_client import LLMClient
from backend.services.user_service import UserService
from backend.services.subscription_service import SubscriptionService
from backend.services.waitlist_service import WaitlistService


# Database Client Provider
def get_service_db_client() -> Client:
    """
    Provides service-level Supabase client.

    This client uses the service role key and bypasses RLS policies.
    Used for all database operations in the service layer.

    Returns:
        Supabase client configured with service role credentials
    """
    return db_client.get_service_client()


# Configuration Providers
def get_stripe_config() -> StripeConfig:
    """Provides Stripe configuration from environment variables."""
    return StripeConfig.from_env()


def get_email_config() -> EmailConfig:
    """Provides Email configuration from environment variables."""
    return EmailConfig.from_env()


def get_github_config() -> GitHubConfig:
    """Provides GitHub configuration from environment variables."""
    return GitHubConfig.from_env()


def get_llm_config() -> LLMConfig:
    """Provides LLM configuration from environment variables."""
    return LLMConfig.from_env()


# Integration Client Providers
def get_stripe_client(
    config: Annotated[StripeConfig, Depends(get_stripe_config)]
) -> StripeClient:
    """Provides Stripe client instance with injected configuration."""
    return StripeClient(config)


def get_email_client(
    config: Annotated[EmailConfig, Depends(get_email_config)]
) -> EmailClient:
    """Provides Email client instance with injected configuration."""
    return EmailClient(config)


def get_github_client(
    config: Annotated[GitHubConfig, Depends(get_github_config)]
) -> GitHubClient:
    """Provides GitHub client instance with injected configuration."""
    return GitHubClient(config)


def get_llm_client(
    config: Annotated[LLMConfig, Depends(get_llm_config)]
) -> LLMClient:
    """Provides LLM client instance with injected configuration."""
    return LLMClient(config)


# Business Service Providers
def get_user_service(
    stripe_client: Annotated[StripeClient, Depends(get_stripe_client)]
) -> UserService:
    """Provides UserService instance with injected dependencies."""
    return UserService(stripe_client=stripe_client)


def get_subscription_service(
    stripe_client: Annotated[StripeClient, Depends(get_stripe_client)]
) -> SubscriptionService:
    """Provides SubscriptionService instance with injected dependencies."""
    return SubscriptionService(stripe_client=stripe_client)


def get_waitlist_service(
    email_client: Annotated[EmailClient, Depends(get_email_client)]
) -> WaitlistService:
    """Provides WaitlistService instance with injected dependencies."""
    return WaitlistService(email_client=email_client)


# Note: Portfolio, Project, Auth, MFA services will be added once they're refactored
# from static methods to instance methods


# Type Aliases for Cleaner Router Signatures
# These provide syntactic sugar for dependency injection in routers

# Database
ServiceDBClient = Annotated[Client, Depends(get_service_db_client)]

# Integration Clients
StripeClientDep = Annotated[StripeClient, Depends(get_stripe_client)]
EmailClientDep = Annotated[EmailClient, Depends(get_email_client)]
GitHubClientDep = Annotated[GitHubClient, Depends(get_github_client)]
LLMClientDep = Annotated[LLMClient, Depends(get_llm_client)]

# Business Services
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
SubscriptionServiceDep = Annotated[SubscriptionService, Depends(get_subscription_service)]
WaitlistServiceDep = Annotated[WaitlistService, Depends(get_waitlist_service)]

# To be added: PortfolioServiceDep, ProjectServiceDep, AuthServiceDep, MFAServiceDep
