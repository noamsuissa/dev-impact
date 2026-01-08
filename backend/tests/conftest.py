"""
Pytest configuration and fixtures for backend tests
"""

import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import pytest
from supabase import Client

# Add the parent directory to Python path so we can import 'backend'
backend_dir = Path(__file__).parent.parent
parent_dir = backend_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from backend.core.config import StripeConfig, EmailConfig, GitHubConfig, LLMConfig
from backend.integrations.stripe_client import StripeClient
from backend.integrations.email_client import EmailClient
from backend.integrations.github_client import GitHubClient
from backend.integrations.llm_client import LLMClient


# ============================================
# Configuration Fixtures
# ============================================


@pytest.fixture
def stripe_config():
    """Mock Stripe configuration"""
    return StripeConfig(
        secret_key="sk_test_mock",
        publishable_key="pk_test_mock",
        price_id_monthly="price_test_monthly",
        price_id_yearly="price_test_yearly",
        webhook_secret="whsec_test_mock",
    )


@pytest.fixture
def email_config():
    """Mock Email configuration"""
    return EmailConfig(
        host="smtp.test.com",
        port=587,
        user="test@example.com",
        password="test_password",
        from_email="noreply@test.com",
        from_name="Test App",
    )


@pytest.fixture
def github_config():
    """Mock GitHub configuration"""
    return GitHubConfig(
        client_id="test_client_id",
        device_auth_url="https://github.com/login/device/code",
        token_url="https://github.com/login/oauth/access_token",
        user_api_url="https://api.github.com/user",
    )


@pytest.fixture
def llm_config():
    """Mock LLM configuration"""
    return LLMConfig(
        openrouter_api_key="sk_test_openrouter",
        openrouter_model="test-model",
        groq_api_key="gsk_test_groq",
        groq_model="test-groq-model",
    )


# ============================================
# Database Client Fixtures
# ============================================


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client"""
    client = Mock(spec=Client)

    # Mock common methods
    client.table = Mock(return_value=Mock())
    client.auth = Mock()
    client.storage = Mock()
    client.postgrest = Mock()

    return client


# ============================================
# Integration Client Fixtures
# ============================================


@pytest.fixture
def mock_stripe_client():
    """Mock Stripe client"""
    client = Mock(spec=StripeClient)

    # Mock async methods
    client.create_checkout_session = AsyncMock()
    client.cancel_subscription = AsyncMock()
    client.get_subscription_info = AsyncMock()
    client.handle_webhook_event = AsyncMock()

    return client


@pytest.fixture
def mock_email_client():
    """Mock Email client"""
    client = Mock(spec=EmailClient)

    # Mock async methods
    client.send_email = AsyncMock()

    return client


@pytest.fixture
def mock_github_client():
    """Mock GitHub client"""
    client = Mock(spec=GitHubClient)

    # Mock async methods
    client.initiate_device_flow = AsyncMock()
    client.poll_for_token = AsyncMock()
    client.get_user_profile = AsyncMock()

    return client


@pytest.fixture
def mock_llm_client():
    """Mock LLM client"""
    client = Mock(spec=LLMClient)

    # Mock async methods
    client.generate_completion = AsyncMock()
    client.get_available_models = Mock(return_value={})
    client.get_providers_status = Mock(return_value={})

    return client


# ============================================
# Service Fixtures
# ============================================


@pytest.fixture
def user_service(mock_stripe_client):
    """UserService instance with mocked dependencies"""
    from backend.services.user_service import UserService

    return UserService(stripe_client=mock_stripe_client)


@pytest.fixture
def subscription_service(mock_stripe_client):
    """SubscriptionService instance with mocked dependencies"""
    from backend.services.subscription_service import SubscriptionService

    return SubscriptionService(stripe_client=mock_stripe_client)


@pytest.fixture
def waitlist_service(mock_email_client):
    """WaitlistService instance with mocked dependencies"""
    from backend.services.waitlist_service import WaitlistService

    return WaitlistService(email_client=mock_email_client)


@pytest.fixture
def portfolio_service():
    """PortfolioService instance"""
    from backend.services.portfolio_service import PortfolioService

    return PortfolioService()


@pytest.fixture
def project_service():
    """ProjectService instance"""
    from backend.services.project_service import ProjectService

    return ProjectService()


@pytest.fixture
def auth_service():
    """AuthService instance"""
    from backend.services.auth.auth_service import AuthService

    return AuthService()


@pytest.fixture
def mfa_service():
    """MFAService instance"""
    from backend.services.auth.mfa_service import MFAService

    return MFAService()
