"""Centralized configuration classes for all services.
All configuration is loaded from environment variables.
"""

import os
from dataclasses import dataclass


@dataclass
class StripeConfig:
    """Stripe payment configuration"""

    secret_key: str
    publishable_key: str
    price_id_monthly: str
    price_id_yearly: str
    webhook_secret: str

    @classmethod
    def from_env(cls) -> "StripeConfig":
        """Load Stripe configuration from environment variables."""
        # Get price IDs with fallback for backward compatibility
        price_id_monthly = os.getenv("STRIPE_PRICE_ID_MONTHLY") or os.getenv("STRIPE_PRICE_ID", "")
        price_id_yearly = os.getenv("STRIPE_PRICE_ID_YEARLY") or os.getenv("STRIPE_PRICE_ID", "")

        return cls(
            secret_key=os.getenv("STRIPE_SECRET_KEY", ""),
            publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY", ""),
            price_id_monthly=price_id_monthly,
            price_id_yearly=price_id_yearly,
            webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET", ""),
        )


@dataclass
class EmailConfig:
    """SMTP email configuration"""

    host: str
    port: int
    user: str
    password: str
    from_email: str
    from_name: str
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> "EmailConfig":
        """Load email configuration from environment variables."""
        return cls(
            host=os.getenv("SMTP_HOST", ""),
            port=int(os.getenv("SMTP_PORT", "587")),
            user=os.getenv("SMTP_USER", ""),
            password=os.getenv("SMTP_PASSWORD", ""),
            from_email=os.getenv("FROM_EMAIL", ""),
            from_name=os.getenv("FROM_NAME", ""),
        )


@dataclass
class GitHubConfig:
    """GitHub OAuth configuration"""

    client_id: str
    device_auth_url: str
    token_url: str
    user_api_url: str

    @classmethod
    def from_env(cls) -> "GitHubConfig":
        """Load GitHub configuration from environment variables."""
        return cls(
            client_id=os.getenv("GITHUB_CLIENT_ID", ""),
            device_auth_url=os.getenv("GITHUB_DEVICE_AUTH_URL", "https://github.com/login/device/code"),
            token_url=os.getenv("GITHUB_TOKEN_URL", "https://github.com/login/oauth/access_token"),
            user_api_url=os.getenv("GITHUB_USER_API_URL", "https://api.github.com/user"),
        )


@dataclass
class LLMConfig:
    """LLM provider configuration"""

    openrouter_api_key: str
    openrouter_model: str
    groq_api_key: str
    groq_model: str

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load LLM configuration from environment variables."""
        return cls(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            openrouter_model=os.getenv("OPENROUTER_MODEL", ""),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            groq_model=os.getenv("GROQ_MODEL", ""),
        )
