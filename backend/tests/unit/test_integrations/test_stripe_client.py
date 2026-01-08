"""
Unit tests for StripeClient integration
Tests the Stripe SDK wrapper with mocked Stripe calls
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.integrations.stripe_client import StripeClient
from backend.core.config import StripeConfig


class TestStripeClient:
    """Test suite for StripeClient"""

    def test_initialization(self, stripe_config):
        """Test Stripe client initializes with config"""
        client = StripeClient(stripe_config)

        assert client.config == stripe_config
        assert client.config.secret_key == "sk_test_mock"

    @pytest.mark.asyncio
    @patch("backend.integrations.stripe_client.stripe.checkout.Session.create")
    async def test_create_checkout_session_monthly(
        self, mock_stripe_create, stripe_config, mock_supabase_client
    ):
        """Test creating monthly checkout session"""
        # Setup mock
        mock_stripe_create.return_value = Mock(
            id="cs_test_123", url="https://checkout.stripe.com/test"
        )

        client = StripeClient(stripe_config)

        # Execute
        result = await client.create_checkout_session(
            client=mock_supabase_client,
            user_id="user_123",
            user_email="test@example.com",
            success_url="https://app.com/success",
            cancel_url="https://app.com/cancel",
            billing_period="monthly",
        )

        # Assert
        assert result["session_id"] == "cs_test_123"
        assert result["checkout_url"] == "https://checkout.stripe.com/test"
        mock_stripe_create.assert_called_once()

        # Verify correct price ID was used
        call_kwargs = mock_stripe_create.call_args[1]
        assert call_kwargs["line_items"][0]["price"] == stripe_config.price_id_monthly

    @pytest.mark.asyncio
    @patch("backend.integrations.stripe_client.stripe.checkout.Session.create")
    async def test_create_checkout_session_yearly(
        self, mock_stripe_create, stripe_config, mock_supabase_client
    ):
        """Test creating yearly checkout session"""
        # Setup mock
        mock_stripe_create.return_value = Mock(
            id="cs_test_456", url="https://checkout.stripe.com/test_yearly"
        )

        client = StripeClient(stripe_config)

        # Execute
        result = await client.create_checkout_session(
            client=mock_supabase_client,
            user_id="user_456",
            user_email="test@example.com",
            success_url="https://app.com/success",
            cancel_url="https://app.com/cancel",
            billing_period="yearly",
        )

        # Assert
        assert result["session_id"] == "cs_test_456"

        # Verify correct price ID was used
        call_kwargs = mock_stripe_create.call_args[1]
        assert call_kwargs["line_items"][0]["price"] == stripe_config.price_id_yearly

    @pytest.mark.asyncio
    @patch("backend.integrations.stripe_client.stripe.Subscription.modify")
    async def test_cancel_subscription(
        self, mock_stripe_modify, stripe_config, mock_supabase_client
    ):
        """Test canceling subscription at period end"""
        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = Mock(
            data={"stripe_subscription_id": "sub_test_123"}
        )

        client = StripeClient(stripe_config)

        # Execute
        await client.cancel_subscription(
            client=mock_supabase_client, user_id="user_123"
        )

        # Assert
        mock_stripe_modify.assert_called_once_with(
            "sub_test_123", cancel_at_period_end=True
        )

    @pytest.mark.asyncio
    async def test_cancel_subscription_no_subscription(
        self, stripe_config, mock_supabase_client
    ):
        """Test canceling when user has no subscription"""
        # Setup mock - no subscription found
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = Mock(
            data=None
        )

        client = StripeClient(stripe_config)

        # Execute - should not raise error
        await client.cancel_subscription(
            client=mock_supabase_client, user_id="user_no_sub"
        )

        # No exception means success

    @pytest.mark.asyncio
    @patch("backend.integrations.stripe_client.stripe.Subscription.retrieve")
    async def test_get_subscription_info(
        self, mock_stripe_retrieve, stripe_config, mock_supabase_client
    ):
        """Test retrieving subscription info"""
        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = Mock(
            data={
                "stripe_subscription_id": "sub_test_123",
                "stripe_customer_id": "cus_test_123",
            }
        )

        mock_stripe_retrieve.return_value = Mock(
            id="sub_test_123",
            status="active",
            current_period_end=1704067200,
            cancel_at_period_end=False,
            items=Mock(
                data=[
                    Mock(
                        price=Mock(id="price_monthly", recurring=Mock(interval="month"))
                    )
                ]
            ),
        )

        client = StripeClient(stripe_config)

        # Execute
        result = await client.get_subscription_info(
            client=mock_supabase_client, user_id="user_123"
        )

        # Assert
        assert result["subscription_id"] == "sub_test_123"
        assert result["status"] == "active"
        assert result["billing_period"] == "monthly"
        assert result["cancel_at_period_end"] is False
