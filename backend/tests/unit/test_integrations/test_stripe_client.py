"""Unit tests for StripeClient integration
Tests the Stripe SDK wrapper with mocked Stripe calls
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from backend.integrations.stripe_client import StripeClient


class TestStripeClient:
    """Test suite for StripeClient"""

    def test_initialization(self, stripe_config):
        """Test Stripe client initializes with config"""
        client = StripeClient(stripe_config)

        assert client.config == stripe_config
        assert client.config.secret_key == "sk_test_mock"

    @pytest.mark.asyncio
    @patch("backend.integrations.stripe_client.stripe.checkout.Session.create")
    async def test_create_checkout_session_monthly(self, mock_stripe_create, stripe_config, mock_supabase_client):
        """Test creating monthly checkout session"""
        # Setup mock
        mock_stripe_create.return_value = Mock(id="cs_test_123", url="https://checkout.stripe.com/test")

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
    async def test_create_checkout_session_yearly(self, mock_stripe_create, stripe_config, mock_supabase_client):
        """Test creating yearly checkout session"""
        # Setup mock
        mock_stripe_create.return_value = Mock(id="cs_test_456", url="https://checkout.stripe.com/test_yearly")

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
    @patch("backend.integrations.stripe_client.stripe.Subscription.list")
    @patch("backend.integrations.stripe_client.stripe.Subscription.modify")
    async def test_cancel_subscription(self, mock_stripe_modify, mock_stripe_list, stripe_config, mock_supabase_client):
        """Test canceling subscription at period end"""
        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = Mock(
            data={"stripe_subscription_id": "sub_test_123"}
        )

        # Mock stripe.Subscription.list to return a subscription
        mock_subscription = Mock(id="sub_test_123", status="active")
        mock_stripe_list.return_value = Mock(data=[mock_subscription])

        client = StripeClient(stripe_config)

        # Execute
        await client.cancel_subscription(client=mock_supabase_client, user_id="user_123")

        # Assert
        mock_stripe_modify.assert_called_once_with("sub_test_123", cancel_at_period_end=True)

    @pytest.mark.asyncio
    @patch("backend.integrations.stripe_client.stripe.Subscription.list")
    async def test_cancel_subscription_no_subscription(self, mock_stripe_list, stripe_config, mock_supabase_client):
        """Test canceling when user has no subscription"""
        # Setup mock - no subscription found in database
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
            data={"stripe_customer_id": "cus_test_123"}
        )

        # Mock stripe.Subscription.list to return empty list (no active subscriptions)
        mock_stripe_list.return_value = Mock(data=[])

        client = StripeClient(stripe_config)

        # Execute - should raise HTTPException when no active subscription found
        with pytest.raises(HTTPException) as exc_info:
            await client.cancel_subscription(client=mock_supabase_client, user_id="user_no_sub")

        assert exc_info.value.status_code == 400
        assert "No active subscription found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_subscription_info(self, stripe_config, mock_supabase_client):
        """Test retrieving subscription info"""
        # Setup mocks - get_subscription_info reads from profiles table
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
            data={
                "subscription_type": "pro",
                "subscription_status": "active",
                "cancel_at_period_end": False,
                "current_period_end": "2024-01-01T00:00:00",
                "stripe_customer_id": "cus_test_123",
            }
        )

        client = StripeClient(stripe_config)

        # Execute
        result = await client.get_subscription_info(client=mock_supabase_client, user_id="user_123")

        # Assert - matches actual return structure
        assert result["subscription_type"] == "pro"
        assert result["subscription_status"] == "active"
        assert result["cancel_at_period_end"] is False
        assert result["has_stripe_customer"] is True
