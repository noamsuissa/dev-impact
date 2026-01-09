"""Tests for PortfolioService"""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from backend.schemas.portfolio import (
    PortfolioResponse,
    PortfolioStatsResponse,
)


class TestGetPublishedPortfolioStats:
    """Tests for get_published_portfolio_stats method"""

    @pytest.mark.asyncio
    async def test_get_published_portfolio_stats_success(self, portfolio_service, mock_supabase_client):
        """Test successful retrieval of portfolio stats"""
        # Arrange
        user_id = "user-123"
        mock_response = MagicMock()
        mock_response.data = [
            {"profile_slug": "portfolio-1", "view_count": 42, "is_published": True},
            {"profile_slug": "portfolio-2", "view_count": 15, "is_published": False},
        ]

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        # Act
        result = await portfolio_service.get_published_portfolio_stats(mock_supabase_client, user_id)

        # Assert
        assert isinstance(result, PortfolioStatsResponse)
        assert len(result.stats) == 2
        assert result.stats[0].portfolio_slug == "portfolio-1"
        assert result.stats[0].view_count == 42
        assert result.stats[0].is_published is True
        assert result.stats[1].portfolio_slug == "portfolio-2"
        assert result.stats[1].view_count == 15
        assert result.stats[1].is_published is False
        mock_supabase_client.table.assert_called_with("published_profiles")
        mock_supabase_client.table.return_value.select.assert_called_with("profile_slug, view_count, is_published")
        mock_supabase_client.table.return_value.select.return_value.eq.assert_called_with("user_id", user_id)

    @pytest.mark.asyncio
    async def test_get_published_portfolio_stats_empty(self, portfolio_service, mock_supabase_client):
        """Test retrieval when user has no published portfolios"""
        # Arrange
        user_id = "user-123"
        mock_response = MagicMock()
        mock_response.data = []

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        # Act
        result = await portfolio_service.get_published_portfolio_stats(mock_supabase_client, user_id)

        # Assert
        assert isinstance(result, PortfolioStatsResponse)
        assert len(result.stats) == 0

    @pytest.mark.asyncio
    async def test_get_published_portfolio_stats_missing_slug(self, portfolio_service, mock_supabase_client):
        """Test handling of missing profile_slug (should default to empty string)"""
        # Arrange
        user_id = "user-123"
        mock_response = MagicMock()
        mock_response.data = [{"profile_slug": None, "view_count": 5, "is_published": True}]

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        # Act
        result = await portfolio_service.get_published_portfolio_stats(mock_supabase_client, user_id)

        # Assert
        assert len(result.stats) == 1
        assert result.stats[0].portfolio_slug == ""

    @pytest.mark.asyncio
    async def test_get_published_portfolio_stats_exception(self, portfolio_service, mock_supabase_client):
        """Test exception handling"""
        # Arrange
        user_id = "user-123"
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await portfolio_service.get_published_portfolio_stats(mock_supabase_client, user_id)
        assert exc_info.value.status_code == 500
        assert "An unexpected error occurred while fetching portfolio stats" in str(exc_info.value.detail)


class TestGetPublishedPortfolio:
    """Tests for get_published_portfolio method with increment flag"""

    @pytest.mark.asyncio
    async def test_get_published_portfolio_increment_true(self, portfolio_service, mock_supabase_client):
        """Test that view count increments when increment_view_count=True"""
        # Arrange
        username = "testuser"
        portfolio_slug = "test-portfolio"
        initial_view_count = 10

        # Mock the select query
        mock_select_response = MagicMock()
        mock_select_response.data = [
            {
                "id": "portfolio-id",
                "username": username,
                "profile_slug": portfolio_slug,
                "view_count": initial_view_count,
                "is_published": True,
                "published_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "profile_data": {
                    "user": {
                        "name": "Test User",
                        "github": {
                            "username": "testuser",
                            "avatar_url": "https://example.com/avatar.jpg",
                        },
                    },
                    "profile": {
                        "name": "Test Portfolio",
                        "description": "Test description",
                    },
                    "projects": [],
                },
            }
        ]

        # Mock the update query
        mock_update_response = MagicMock()

        # Set up the mock chain
        # The query object returns itself on each method call (fluent interface)
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query  # Each .eq() returns the same query object
        mock_query.execute.return_value = mock_select_response

        mock_table = MagicMock()
        mock_table.select.return_value = mock_query

        # Set up update chain
        mock_update_query = MagicMock()
        mock_update_query.eq.return_value = mock_update_query  # Each .eq() returns the same query object
        mock_update_query.execute.return_value = mock_update_response

        mock_supabase_client.table.return_value = mock_table
        mock_table.update.return_value = mock_update_query

        # Act
        result = await portfolio_service.get_published_portfolio(mock_supabase_client, username, portfolio_slug, increment_view_count=True)

        # Assert
        assert isinstance(result, PortfolioResponse)
        assert result.view_count == initial_view_count + 1
        assert result.username == username
        assert result.portfolio_slug == portfolio_slug
        # Verify update was called
        mock_table.update.assert_called_with({"view_count": initial_view_count + 1})

    @pytest.mark.asyncio
    async def test_get_published_portfolio_increment_false(self, portfolio_service, mock_supabase_client):
        """Test that view count does NOT increment when increment_view_count=False"""
        # Arrange
        username = "testuser"
        portfolio_slug = "test-portfolio"
        initial_view_count = 10

        # Mock the select query
        mock_select_response = MagicMock()
        mock_select_response.data = [
            {
                "id": "portfolio-id",
                "username": username,
                "profile_slug": portfolio_slug,
                "view_count": initial_view_count,
                "is_published": True,
                "published_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "profile_data": {
                    "user": {
                        "name": "Test User",
                        "github": {
                            "username": "testuser",
                            "avatar_url": "https://example.com/avatar.jpg",
                        },
                    },
                    "profile": {
                        "name": "Test Portfolio",
                        "description": "Test description",
                    },
                    "projects": [],
                },
            }
        ]

        # Set up the mock chain
        # The query object returns itself on each method call (fluent interface)
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query  # Each .eq() returns the same query object
        mock_query.execute.return_value = mock_select_response

        mock_table = MagicMock()
        mock_table.select.return_value = mock_query

        mock_supabase_client.table.return_value = mock_table

        # Act
        result = await portfolio_service.get_published_portfolio(mock_supabase_client, username, portfolio_slug, increment_view_count=False)

        # Assert
        assert isinstance(result, PortfolioResponse)
        assert result.view_count == initial_view_count  # Should NOT be incremented
        assert result.username == username
        assert result.portfolio_slug == portfolio_slug
        # Verify update was NOT called
        mock_table.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_published_portfolio_increment_default_true(self, portfolio_service, mock_supabase_client):
        """Test that increment_view_count defaults to True"""
        # Arrange
        username = "testuser"
        portfolio_slug = "test-portfolio"
        initial_view_count = 10

        mock_select_response = MagicMock()
        mock_select_response.data = [
            {
                "id": "portfolio-id",
                "username": username,
                "profile_slug": portfolio_slug,
                "view_count": initial_view_count,
                "is_published": True,
                "published_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "profile_data": {
                    "user": {
                        "name": "Test User",
                        "github": {
                            "username": "testuser",
                            "avatar_url": "https://example.com/avatar.jpg",
                        },
                    },
                    "profile": {
                        "name": "Test Portfolio",
                        "description": "Test description",
                    },
                    "projects": [],
                },
            }
        ]

        # Set up the mock chain
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_select_response

        mock_update_query = MagicMock()
        mock_update_query.eq.return_value = mock_update_query
        mock_update_query.execute.return_value = MagicMock()

        mock_table = MagicMock()
        mock_table.select.return_value = mock_query
        mock_table.update.return_value = mock_update_query

        mock_supabase_client.table.return_value = mock_table

        # Act (no increment_view_count parameter, should default to True)
        result = await portfolio_service.get_published_portfolio(mock_supabase_client, username, portfolio_slug)

        # Assert
        assert result.view_count == initial_view_count + 1
        mock_table.update.assert_called()

    @pytest.mark.asyncio
    async def test_get_published_portfolio_not_found(self, portfolio_service, mock_supabase_client):
        """Test error when portfolio not found"""
        # Arrange
        username = "testuser"
        portfolio_slug = "nonexistent"

        mock_select_response = MagicMock()
        mock_select_response.data = []

        # Set up the mock chain
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_select_response

        mock_table = MagicMock()
        mock_table.select.return_value = mock_query

        mock_supabase_client.table.return_value = mock_table

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await portfolio_service.get_published_portfolio(
                mock_supabase_client,
                username,
                portfolio_slug,
                increment_view_count=False,
            )
        assert exc_info.value.status_code == 404
        assert "Portfolio not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_published_portfolio_increment_exception_handled(self, portfolio_service, mock_supabase_client):
        """Test that exception during increment doesn't break the response"""
        # Arrange
        username = "testuser"
        portfolio_slug = "test-portfolio"
        initial_view_count = 10

        mock_select_response = MagicMock()
        mock_select_response.data = [
            {
                "id": "portfolio-id",
                "username": username,
                "profile_slug": portfolio_slug,
                "view_count": initial_view_count,
                "is_published": True,
                "published_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "profile_data": {
                    "user": {
                        "name": "Test User",
                        "github": {
                            "username": "testuser",
                            "avatar_url": "https://example.com/avatar.jpg",
                        },
                    },
                    "profile": {
                        "name": "Test Portfolio",
                        "description": "Test description",
                    },
                    "projects": [],
                },
            }
        ]

        # Set up the mock chain
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_select_response

        # Make update raise an exception
        mock_update_query = MagicMock()
        mock_update_query.eq.return_value = mock_update_query
        mock_update_query.execute.side_effect = Exception("Update failed")

        mock_table = MagicMock()
        mock_table.select.return_value = mock_query
        mock_table.update.return_value = mock_update_query

        mock_supabase_client.table.return_value = mock_table

        # Act
        result = await portfolio_service.get_published_portfolio(mock_supabase_client, username, portfolio_slug, increment_view_count=True)

        # Assert - should still return the portfolio with original view count
        assert isinstance(result, PortfolioResponse)
        assert result.view_count == initial_view_count  # Not incremented due to exception
        assert result.username == username
