"""
Unit tests for SubscriptionService
Tests subscription operations with mocked Stripe client
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from backend.services.subscription_service import SubscriptionService


class TestSubscriptionService:
    """Test suite for SubscriptionService"""

    def test_initialization(self, mock_stripe_client):
        """Test SubscriptionService initializes with injected Stripe client"""
        service = SubscriptionService(stripe_client=mock_stripe_client)

        assert service.stripe_client == mock_stripe_client

    @pytest.mark.asyncio
    async def test_get_subscription_info_with_subscription(
        self, subscription_service, mock_supabase_client, mock_stripe_client
    ):
        """Test getting subscription info for user with active subscription"""
        # Setup mocks
        mock_stripe_client.get_subscription_info = AsyncMock(return_value={
            "subscription_id": "sub_123",
            "status": "active",
            "billing_period": "monthly",
            "current_period_end": 1704067200,
            "cancel_at_period_end": False
        })

        # Execute
        result = await subscription_service.get_subscription_info(
            mock_supabase_client,
            "user_123"
        )

        # Assert
        assert result.plan == "pro"
        assert result.status == "active"
        assert result.billing_period == "monthly"
        assert result.cancel_at_period_end is False

        # Verify limits are set correctly for pro plan
        assert result.max_portfolios == 10
        assert result.max_projects_per_portfolio == 20

    @pytest.mark.asyncio
    async def test_get_subscription_info_free_tier(
        self, subscription_service, mock_supabase_client, mock_stripe_client
    ):
        """Test getting subscription info for free tier user"""
        # Setup mock - no subscription
        mock_stripe_client.get_subscription_info = AsyncMock(return_value=None)

        # Execute
        result = await subscription_service.get_subscription_info(
            mock_supabase_client,
            "user_free"
        )

        # Assert
        assert result.plan == "free"
        assert result.status == "active"
        assert result.billing_period is None

        # Verify limits are set correctly for free plan
        assert result.max_portfolios == 1
        assert result.max_projects_per_portfolio == 3

    @pytest.mark.asyncio
    async def test_cancel_subscription_success(
        self, subscription_service, mock_supabase_client, mock_stripe_client
    ):
        """Test successfully canceling subscription"""
        # Setup mock
        mock_stripe_client.cancel_subscription = AsyncMock()

        # Execute
        result = await subscription_service.cancel_subscription(
            mock_supabase_client,
            "user_123"
        )

        # Assert
        assert result.success is True
        assert "will be canceled" in result.message

        # Verify Stripe client was called
        mock_stripe_client.cancel_subscription.assert_called_once_with(
            mock_supabase_client,
            "user_123"
        )

    @pytest.mark.asyncio
    async def test_cancel_subscription_no_subscription(
        self, subscription_service, mock_supabase_client, mock_stripe_client
    ):
        """Test canceling when user has no subscription"""
        # Setup mock to raise exception
        mock_stripe_client.cancel_subscription = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="No subscription found")
        )

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.cancel_subscription(
                mock_supabase_client,
                "user_no_sub"
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_subscription_info_canceled_subscription(
        self, subscription_service, mock_supabase_client, mock_stripe_client
    ):
        """Test getting info for subscription that's canceled at period end"""
        # Setup mock
        mock_stripe_client.get_subscription_info = AsyncMock(return_value={
            "subscription_id": "sub_456",
            "status": "active",
            "billing_period": "yearly",
            "current_period_end": 1704067200,
            "cancel_at_period_end": True
        })

        # Execute
        result = await subscription_service.get_subscription_info(
            mock_supabase_client,
            "user_456"
        )

        # Assert
        assert result.plan == "pro"
        assert result.status == "active"
        assert result.billing_period == "yearly"
        assert result.cancel_at_period_end is True

    @pytest.mark.asyncio
    async def test_get_subscription_info_expired(
        self, subscription_service, mock_supabase_client, mock_stripe_client
    ):
        """Test getting info for expired subscription"""
        # Setup mock
        mock_stripe_client.get_subscription_info = AsyncMock(return_value={
            "subscription_id": "sub_789",
            "status": "canceled",
            "billing_period": "monthly",
            "current_period_end": 1704067200,
            "cancel_at_period_end": False
        })

        # Execute
        result = await subscription_service.get_subscription_info(
            mock_supabase_client,
            "user_expired"
        )

        # Assert - user should be on free tier if subscription expired
        assert result.plan == "free"
        assert result.status == "canceled"
