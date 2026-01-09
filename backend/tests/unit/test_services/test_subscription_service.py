"""Unit tests for SubscriptionService
Tests subscription operations with mocked Stripe client
"""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from backend.services.subscription_service import SubscriptionService


class TestSubscriptionService:
    """Test suite for SubscriptionService"""

    def test_initialization(self, mock_stripe_client):
        """Test SubscriptionService initializes with injected Stripe client"""
        service = SubscriptionService(stripe_client=mock_stripe_client)

        assert service.stripe_client == mock_stripe_client

    @pytest.mark.asyncio
    async def test_get_subscription_info_with_subscription(self, subscription_service, mock_supabase_client, mock_stripe_client):
        """Test getting subscription info for user with active subscription"""
        # Setup mocks
        mock_stripe_client.get_subscription_info = AsyncMock(
            return_value={
                "subscription_id": "sub_123",
                "status": "active",
                "billing_period": "monthly",
                "current_period_end": 1704067200,
                "cancel_at_period_end": False,
            }
        )

        # Mock profile query
        mock_profile = Mock()
        mock_profile.data = {"subscription_type": "pro", "subscription_status": "active"}
        mock_profile_query = Mock()
        mock_profile_query.eq.return_value = mock_profile_query
        mock_profile_query.single.return_value = mock_profile_query
        mock_profile_query.execute.return_value = mock_profile

        # Mock portfolio count query - data must be a list for len() to work
        mock_portfolio_count = Mock()
        mock_portfolio_count.data = [{"id": "p1"}, {"id": "p2"}]  # List, not Mock
        mock_portfolio_count_query = Mock()
        mock_portfolio_count_query.select.return_value = mock_portfolio_count_query
        mock_portfolio_count_query.eq.return_value = mock_portfolio_count_query
        mock_portfolio_count_query.execute.return_value = mock_portfolio_count

        # Mock project count query - data must be a list for len() to work
        mock_project_count = Mock()
        mock_project_count.data = [{"id": "pr1"}]  # List, not Mock
        mock_project_count_query = Mock()
        mock_project_count_query.select.return_value = mock_project_count_query
        mock_project_count_query.eq.return_value = mock_project_count_query
        mock_project_count_query.execute.return_value = mock_project_count

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                mock_table.select.return_value = mock_profile_query
            elif table_name == "portfolios":
                mock_table.select.return_value = mock_portfolio_count_query
            elif table_name == "impact_projects":
                mock_table.select.return_value = mock_project_count_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        result = await subscription_service.get_subscription_info(mock_supabase_client, "user_123")

        # Assert - SubscriptionInfoResponse uses subscription_type, not plan
        assert result.subscription_type == "pro"
        assert result.subscription_status == "active"
        assert result.cancel_at_period_end is False

        # Verify limits are set correctly for pro plan
        assert result.max_portfolios == 1000  # Unlimited for pro
        assert result.max_projects == 1000  # Unlimited for pro

    @pytest.mark.asyncio
    async def test_get_subscription_info_free_tier(self, subscription_service, mock_supabase_client, mock_stripe_client):
        """Test getting subscription info for free tier user"""
        # Setup mock - no subscription
        mock_stripe_client.get_subscription_info = AsyncMock(return_value=None)

        # Mock profile query
        mock_profile = Mock()
        mock_profile.data = {"subscription_type": "free"}
        mock_profile_query = Mock()
        mock_profile_query.eq.return_value = mock_profile_query
        mock_profile_query.single.return_value = mock_profile_query
        mock_profile_query.execute.return_value = mock_profile

        # Mock portfolio count query - data must be a list for len() to work
        mock_portfolio_count = Mock()
        mock_portfolio_count.data = []  # Empty list, not Mock
        mock_portfolio_count_query = Mock()
        mock_portfolio_count_query.select.return_value = mock_portfolio_count_query
        mock_portfolio_count_query.eq.return_value = mock_portfolio_count_query
        mock_portfolio_count_query.execute.return_value = mock_portfolio_count

        # Mock project count query - data must be a list for len() to work
        mock_project_count = Mock()
        mock_project_count.data = []  # Empty list, not Mock
        mock_project_count_query = Mock()
        mock_project_count_query.select.return_value = mock_project_count_query
        mock_project_count_query.eq.return_value = mock_project_count_query
        mock_project_count_query.execute.return_value = mock_project_count

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                mock_table.select.return_value = mock_profile_query
            elif table_name == "portfolios":
                mock_table.select.return_value = mock_portfolio_count_query
            elif table_name == "impact_projects":
                mock_table.select.return_value = mock_project_count_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        result = await subscription_service.get_subscription_info(mock_supabase_client, "user_free")

        # Assert - SubscriptionInfoResponse uses subscription_type, not plan
        assert result.subscription_type == "free"
        assert result.subscription_status is None

        # Verify limits are set correctly for free plan
        assert result.max_portfolios == 1
        assert result.max_projects == 10  # Free users limited to 10 projects

    @pytest.mark.asyncio
    async def test_cancel_subscription_success(self, subscription_service, mock_supabase_client, mock_stripe_client):
        """Test successfully canceling subscription"""
        # Setup mock
        mock_stripe_client.cancel_subscription = AsyncMock()

        # Execute
        result = await subscription_service.cancel_subscription(mock_supabase_client, "user_123")

        # Assert
        assert result.success is True
        assert "canceled" in result.message.lower() or "cancellation" in result.message.lower()

        # Verify Stripe client was called
        mock_stripe_client.cancel_subscription.assert_called_once_with(mock_supabase_client, "user_123")

    @pytest.mark.asyncio
    async def test_cancel_subscription_no_subscription(self, subscription_service, mock_supabase_client, mock_stripe_client):
        """Test canceling when user has no subscription"""
        # Setup mock to raise exception
        mock_stripe_client.cancel_subscription = AsyncMock(side_effect=HTTPException(status_code=404, detail="No subscription found"))

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.cancel_subscription(mock_supabase_client, "user_no_sub")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_subscription_info_canceled_subscription(self, subscription_service, mock_supabase_client, mock_stripe_client):
        """Test getting info for subscription that's canceled at period end"""
        # Setup mock
        mock_stripe_client.get_subscription_info = AsyncMock(
            return_value={
                "subscription_id": "sub_456",
                "status": "active",
                "billing_period": "yearly",
                "current_period_end": 1704067200,
                "cancel_at_period_end": True,
            }
        )

        # Mock profile query
        mock_profile = Mock()
        mock_profile.data = {"subscription_type": "pro", "subscription_status": "active", "cancel_at_period_end": True}
        mock_profile_query = Mock()
        mock_profile_query.eq.return_value = mock_profile_query
        mock_profile_query.single.return_value = mock_profile_query
        mock_profile_query.execute.return_value = mock_profile

        # Mock portfolio count query - data must be a list for len() to work
        mock_portfolio_count = Mock()
        mock_portfolio_count.data = []  # List, not Mock
        mock_portfolio_count_query = Mock()
        mock_portfolio_count_query.select.return_value = mock_portfolio_count_query
        mock_portfolio_count_query.eq.return_value = mock_portfolio_count_query
        mock_portfolio_count_query.execute.return_value = mock_portfolio_count

        # Mock project count query - data must be a list for len() to work
        mock_project_count = Mock()
        mock_project_count.data = []  # List, not Mock
        mock_project_count_query = Mock()
        mock_project_count_query.select.return_value = mock_project_count_query
        mock_project_count_query.eq.return_value = mock_project_count_query
        mock_project_count_query.execute.return_value = mock_project_count

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                mock_table.select.return_value = mock_profile_query
            elif table_name == "portfolios":
                mock_table.select.return_value = mock_portfolio_count_query
            elif table_name == "impact_projects":
                mock_table.select.return_value = mock_project_count_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        result = await subscription_service.get_subscription_info(mock_supabase_client, "user_456")

        # Assert - SubscriptionInfoResponse uses subscription_type, not plan
        assert result.subscription_type == "pro"
        assert result.subscription_status == "active"
        assert result.cancel_at_period_end is True

    @pytest.mark.asyncio
    async def test_get_subscription_info_expired(self, subscription_service, mock_supabase_client, mock_stripe_client):
        """Test getting info for expired subscription"""
        # Setup mock
        mock_stripe_client.get_subscription_info = AsyncMock(
            return_value={
                "subscription_id": "sub_789",
                "status": "canceled",
                "billing_period": "monthly",
                "current_period_end": 1704067200,
                "cancel_at_period_end": False,
            }
        )

        # Mock profile query
        mock_profile = Mock()
        mock_profile.data = {"subscription_type": "free", "subscription_status": "canceled"}
        mock_profile_query = Mock()
        mock_profile_query.eq.return_value = mock_profile_query
        mock_profile_query.single.return_value = mock_profile_query
        mock_profile_query.execute.return_value = mock_profile

        # Mock portfolio count query - data must be a list for len() to work
        mock_portfolio_count = Mock()
        mock_portfolio_count.data = []  # List, not Mock
        mock_portfolio_count_query = Mock()
        mock_portfolio_count_query.select.return_value = mock_portfolio_count_query
        mock_portfolio_count_query.eq.return_value = mock_portfolio_count_query
        mock_portfolio_count_query.execute.return_value = mock_portfolio_count

        # Mock project count query - data must be a list for len() to work
        mock_project_count = Mock()
        mock_project_count.data = []  # List, not Mock
        mock_project_count_query = Mock()
        mock_project_count_query.select.return_value = mock_project_count_query
        mock_project_count_query.eq.return_value = mock_project_count_query
        mock_project_count_query.execute.return_value = mock_project_count

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                mock_table.select.return_value = mock_profile_query
            elif table_name == "portfolios":
                mock_table.select.return_value = mock_portfolio_count_query
            elif table_name == "impact_projects":
                mock_table.select.return_value = mock_project_count_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        result = await subscription_service.get_subscription_info(mock_supabase_client, "user_expired")

        # Assert - user should be on free tier if subscription expired
        assert result.subscription_type == "free"
        assert result.subscription_status == "canceled"
