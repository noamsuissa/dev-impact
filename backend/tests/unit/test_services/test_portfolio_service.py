"""
Unit tests for PortfolioService
Tests business logic with mocked dependencies
"""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from backend.schemas.portfolio import Portfolio, PortfolioResponse, PortfolioStatsResponse, PublishPortfolioResponse
from backend.services.portfolio_service import PortfolioService


class TestPortfolioService:
    """Test suite for PortfolioService"""

    def test_initialization(self):
        """Test PortfolioService initializes correctly"""
        service = PortfolioService()
        assert service is not None

    def test_validate_username_valid(self, portfolio_service):
        """Test username validation with valid usernames"""
        assert portfolio_service.validate_username("validuser") is True
        assert portfolio_service.validate_username("user-123") is True
        assert portfolio_service.validate_username("my-username") is True
        assert portfolio_service.validate_username("a" * 50) is True  # Max length

    def test_validate_username_invalid(self, portfolio_service):
        """Test username validation with invalid usernames"""
        assert portfolio_service.validate_username("") is False  # Empty
        assert portfolio_service.validate_username("ab") is False  # Too short
        assert portfolio_service.validate_username("a" * 51) is False  # Too long
        assert portfolio_service.validate_username("User Name") is False  # Spaces
        assert portfolio_service.validate_username("USER") is False  # Uppercase
        assert portfolio_service.validate_username("user@name") is False  # Special chars

    def test_generate_slug(self, portfolio_service):
        """Test slug generation from names"""
        assert portfolio_service.generate_slug("My Portfolio") == "my-portfolio"
        assert portfolio_service.generate_slug("Test 123") == "test-123"
        assert portfolio_service.generate_slug("Hello-World") == "hello-world"
        assert portfolio_service.generate_slug("") == "portfolio"  # Empty defaults
        assert portfolio_service.generate_slug("   ") == "portfolio"  # Whitespace only

    def test_validate_slug(self, portfolio_service):
        """Test slug validation"""
        assert portfolio_service.validate_slug("valid-slug") is True
        assert portfolio_service.validate_slug("slug123") is True
        assert portfolio_service.validate_slug("a") is True  # Min length
        assert portfolio_service.validate_slug("a" * 100) is True  # Max length
        assert portfolio_service.validate_slug("") is False  # Empty
        assert portfolio_service.validate_slug("Invalid Slug") is False  # Spaces
        assert portfolio_service.validate_slug("INVALID") is False  # Uppercase

    @pytest.mark.asyncio
    async def test_create_portfolio_success(self, portfolio_service, mock_supabase_client, subscription_info):
        """Test successful portfolio creation"""
        # Setup mocks
        subscription_info.can_add_portfolio = True
        subscription_info.max_portfolios = 10

        # Mock slug uniqueness check - no existing portfolio
        mock_slug_check = Mock()
        mock_slug_check.data = []
        mock_slug_query = Mock()
        mock_slug_query.eq.return_value = mock_slug_query
        mock_slug_query.execute.return_value = mock_slug_check

        # Mock count query
        mock_count = Mock()
        mock_count.data = []
        mock_count_query = Mock()
        mock_count_query.select.return_value = mock_count_query
        mock_count_query.eq.return_value = mock_count_query
        mock_count_query.execute.return_value = mock_count

        # Mock insert
        mock_insert = Mock()
        mock_insert.data = [
            {
                "id": "portfolio_123",
                "name": "My Portfolio",
                "description": "Test description",
                "slug": "my-portfolio",
                "display_order": 0,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        ]
        mock_insert_query = Mock()
        mock_insert_query.execute.return_value = mock_insert

        # Setup table mock
        mock_table = Mock()
        mock_table.select.return_value = mock_slug_query
        mock_table.insert.return_value = mock_insert_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await portfolio_service.create_portfolio(
            mock_supabase_client, subscription_info, "user_123", "My Portfolio", "Test description"
        )

        # Assert
        assert isinstance(result, Portfolio)
        assert result.id == "portfolio_123"
        assert result.name == "My Portfolio"
        assert result.slug == "my-portfolio"

    @pytest.mark.asyncio
    async def test_create_portfolio_limit_reached(self, portfolio_service, mock_supabase_client, subscription_info):
        """Test portfolio creation when limit is reached"""
        subscription_info.can_add_portfolio = False
        subscription_info.max_portfolios = 1

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await portfolio_service.create_portfolio(mock_supabase_client, subscription_info, "user_123", "My Portfolio")

        assert exc_info.value.status_code == 403
        assert "Portfolio limit reached" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_portfolio_duplicate_slug(self, portfolio_service, mock_supabase_client, subscription_info):
        """Test slug uniqueness handling"""
        subscription_info.can_add_portfolio = True

        # Mock slug check - first check finds existing, second doesn't
        mock_slug_check1 = Mock()
        mock_slug_check1.data = [{"id": "existing"}]
        mock_slug_check2 = Mock()
        mock_slug_check2.data = []

        mock_slug_query = Mock()
        mock_slug_query.eq.return_value = mock_slug_query
        # First call returns existing, second call returns empty
        mock_slug_query.execute.side_effect = [mock_slug_check1, mock_slug_check2]

        # Mock count
        mock_count = Mock()
        mock_count.data = []
        mock_count_query = Mock()
        mock_count_query.select.return_value = mock_count_query
        mock_count_query.eq.return_value = mock_count_query
        mock_count_query.execute.return_value = mock_count

        # Mock insert
        mock_insert = Mock()
        mock_insert.data = [
            {
                "id": "portfolio_123",
                "name": "My Portfolio",
                "slug": "my-portfolio-1",
                "display_order": 0,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        ]
        mock_insert_query = Mock()
        mock_insert_query.execute.return_value = mock_insert

        mock_table = Mock()
        mock_table.select.return_value = mock_slug_query
        mock_table.insert.return_value = mock_insert_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await portfolio_service.create_portfolio(mock_supabase_client, subscription_info, "user_123", "My Portfolio")

        # Assert slug has counter appended
        assert result.slug == "my-portfolio-1"

    @pytest.mark.asyncio
    async def test_list_portfolios(self, portfolio_service, mock_supabase_client):
        """Test listing all user portfolios"""
        # Setup mock
        mock_response = Mock()
        mock_response.data = [
            {
                "id": "portfolio_1",
                "name": "Portfolio 1",
                "description": "Desc 1",
                "slug": "portfolio-1",
                "display_order": 0,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
            {
                "id": "portfolio_2",
                "name": "Portfolio 2",
                "slug": "portfolio-2",
                "display_order": 1,
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
            },
        ]

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = mock_response

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await portfolio_service.list_portfolios(mock_supabase_client, "user_123")

        # Assert
        assert len(result) == 2
        assert result[0].name == "Portfolio 1"
        assert result[1].name == "Portfolio 2"

    @pytest.mark.asyncio
    async def test_get_portfolio_success(self, portfolio_service, mock_supabase_client):
        """Test getting a single portfolio"""
        # Setup mock
        mock_response = Mock()
        mock_response.data = {
            "id": "portfolio_123",
            "name": "My Portfolio",
            "description": "Test",
            "slug": "my-portfolio",
            "display_order": 0,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.single.return_value = mock_query
        mock_query.execute.return_value = mock_response

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await portfolio_service.get_portfolio(mock_supabase_client, "portfolio_123", "user_123")

        # Assert
        assert isinstance(result, Portfolio)
        assert result.id == "portfolio_123"
        assert result.name == "My Portfolio"

    @pytest.mark.asyncio
    async def test_get_portfolio_not_found(self, portfolio_service, mock_supabase_client):
        """Test getting portfolio that doesn't exist"""
        # Setup mock - no portfolio found
        mock_response = Mock()
        mock_response.data = None

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.single.return_value = mock_query
        mock_query.execute.return_value = mock_response

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_supabase_client.table.return_value = mock_table

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await portfolio_service.get_portfolio(mock_supabase_client, "nonexistent", "user_123")

        assert exc_info.value.status_code == 404
        assert "Portfolio not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_portfolio(self, portfolio_service, mock_supabase_client):
        """Test updating portfolio"""
        # Setup mocks - ownership check
        mock_ownership = Mock()
        mock_ownership.data = [{"user_id": "user_123", "slug": "old-slug"}]

        mock_ownership_query = Mock()
        mock_ownership_query.select.return_value = mock_ownership_query
        mock_ownership_query.eq.return_value = mock_ownership_query
        mock_ownership_query.execute.return_value = mock_ownership

        # Mock slug uniqueness check
        mock_slug_check = Mock()
        mock_slug_check.data = []

        mock_slug_query = Mock()
        mock_slug_query.eq.return_value = mock_slug_query
        mock_slug_query.neq.return_value = mock_slug_query
        mock_slug_query.execute.return_value = mock_slug_check

        # Mock update
        mock_update = Mock()
        mock_update.data = [
            {
                "id": "portfolio_123",
                "name": "Updated Name",
                "description": "Updated description",
                "slug": "updated-name",
                "display_order": 0,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
            }
        ]

        mock_update_query = Mock()
        mock_update_query.eq.return_value = mock_update_query
        mock_update_query.execute.return_value = mock_update

        mock_table = Mock()
        mock_table.select.return_value = mock_ownership_query
        mock_table.update.return_value = mock_update_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await portfolio_service.update_portfolio(
            mock_supabase_client, "portfolio_123", "user_123", name="Updated Name", description="Updated description"
        )

        # Assert
        assert result.name == "Updated Name"
        assert result.description == "Updated description"

    @pytest.mark.asyncio
    async def test_update_portfolio_unauthorized(self, portfolio_service, mock_supabase_client):
        """Test updating portfolio with wrong user"""
        # Setup mock - different user_id
        mock_ownership = Mock()
        mock_ownership.data = [{"user_id": "other_user", "slug": "old-slug"}]

        mock_ownership_query = Mock()
        mock_ownership_query.select.return_value = mock_ownership_query
        mock_ownership_query.eq.return_value = mock_ownership_query
        mock_ownership_query.execute.return_value = mock_ownership

        mock_table = Mock()
        mock_table.select.return_value = mock_ownership_query
        mock_supabase_client.table.return_value = mock_table

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await portfolio_service.update_portfolio(mock_supabase_client, "portfolio_123", "user_123", name="Updated Name")

        assert exc_info.value.status_code == 403
        assert "permission" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_delete_portfolio(self, portfolio_service, mock_supabase_client):
        """Test deleting portfolio"""
        # Setup mocks - ownership check
        mock_ownership = Mock()
        mock_ownership.data = [{"user_id": "user_123"}]

        mock_ownership_query = Mock()
        mock_ownership_query.select.return_value = mock_ownership_query
        mock_ownership_query.eq.return_value = mock_ownership_query
        mock_ownership_query.execute.return_value = mock_ownership

        # Mock delete projects
        mock_delete_projects_query = Mock()
        mock_delete_projects_query.eq.return_value = mock_delete_projects_query
        mock_delete_projects_query.execute.return_value = Mock()

        # Mock delete portfolio
        mock_delete_query = Mock()
        mock_delete_query.eq.return_value = mock_delete_query
        mock_delete_query.execute.return_value = Mock()

        # Setup table mocks
        mock_projects_table = Mock()
        mock_projects_table.delete.return_value = mock_delete_projects_query

        mock_portfolio_table = Mock()
        mock_portfolio_table.select.return_value = mock_ownership_query
        mock_portfolio_table.delete.return_value = mock_delete_query

        def table_side_effect(table_name):
            if table_name == "impact_projects":
                return mock_projects_table
            return mock_portfolio_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        result = await portfolio_service.delete_portfolio(mock_supabase_client, "portfolio_123", "user_123")

        # Assert
        assert result.success is True
        assert "deleted successfully" in result.message

    @pytest.mark.asyncio
    async def test_publish_portfolio(self, portfolio_service, mock_supabase_client, mock_user_profile, mock_projects):
        """Test publishing portfolio"""
        # Setup mocks
        mock_portfolio = Mock()
        mock_portfolio.data = {"id": "portfolio_123", "slug": "my-portfolio", "name": "My Portfolio", "description": "Test"}

        mock_portfolio_query = Mock()
        mock_portfolio_query.eq.return_value = mock_portfolio_query
        mock_portfolio_query.single.return_value = mock_portfolio_query
        mock_portfolio_query.execute.return_value = mock_portfolio

        # Mock existing check
        mock_existing = Mock()
        mock_existing.data = []

        mock_existing_query = Mock()
        mock_existing_query.eq.return_value = mock_existing_query
        mock_existing_query.execute.return_value = mock_existing

        # Mock insert
        mock_insert = Mock()
        mock_insert.data = [
            {
                "id": "published_123",
                "username": "testuser",
                "portfolio_id": "portfolio_123",
                "profile_slug": "my-portfolio",
                "is_published": True,
            }
        ]

        mock_insert_query = Mock()
        mock_insert_query.execute.return_value = mock_insert

        mock_table = Mock()
        mock_table.select.return_value = mock_portfolio_query
        mock_table.insert.return_value = mock_insert_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await portfolio_service.publish_portfolio(
            mock_supabase_client, "testuser", "portfolio_123", mock_user_profile, mock_projects, "user_123"
        )

        # Assert
        assert isinstance(result, PublishPortfolioResponse)
        assert result.success is True
        assert result.username == "testuser"
        assert result.portfolio_slug == "my-portfolio"

    @pytest.mark.asyncio
    async def test_unpublish_portfolio(self, portfolio_service, mock_supabase_client):
        """Test unpublishing portfolio"""
        # Setup mocks
        mock_published = Mock()
        mock_published.data = [{"portfolio_id": "portfolio_123"}]

        mock_published_query = Mock()
        mock_published_query.select.return_value = mock_published_query
        mock_published_query.eq.return_value = mock_published_query
        mock_published_query.execute.return_value = mock_published

        # Mock portfolio ownership check
        mock_portfolio = Mock()
        mock_portfolio.data = {"user_id": "user_123"}

        mock_portfolio_query = Mock()
        mock_portfolio_query.select.return_value = mock_portfolio_query
        mock_portfolio_query.eq.return_value = mock_portfolio_query
        mock_portfolio_query.single.return_value = mock_portfolio_query
        mock_portfolio_query.execute.return_value = mock_portfolio

        # Mock update
        mock_update_query = Mock()
        mock_update_query.eq.return_value = mock_update_query
        mock_update_query.execute.return_value = Mock()

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "portfolios":
                mock_table.select.return_value = mock_portfolio_query
            else:
                mock_table.select.return_value = mock_published_query
                mock_table.update.return_value = mock_update_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        result = await portfolio_service.unpublish_portfolio(mock_supabase_client, "testuser", "my-portfolio", "user_123")

        # Assert
        assert result.success is True
        assert "unpublished" in result.message.lower()

    @pytest.mark.asyncio
    async def test_get_published_portfolio_stats_success(self, portfolio_service, mock_supabase_client):
        """Test successful retrieval of portfolio stats"""
        # Setup mock
        mock_response = Mock()
        mock_response.data = [
            {"profile_slug": "portfolio-1", "view_count": 42, "is_published": True},
            {"profile_slug": "portfolio-2", "view_count": 15, "is_published": False},
        ]

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await portfolio_service.get_published_portfolio_stats(mock_supabase_client, "user_123")

        # Assert
        assert isinstance(result, PortfolioStatsResponse)
        assert len(result.stats) == 2
        assert result.stats[0].portfolio_slug == "portfolio-1"
        assert result.stats[0].view_count == 42
        assert result.stats[0].is_published is True

    @pytest.mark.asyncio
    async def test_get_published_portfolio_stats_empty(self, portfolio_service, mock_supabase_client):
        """Test retrieval when user has no published portfolios"""
        # Setup mock
        mock_response = Mock()
        mock_response.data = []

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await portfolio_service.get_published_portfolio_stats(mock_supabase_client, "user_123")

        # Assert
        assert isinstance(result, PortfolioStatsResponse)
        assert len(result.stats) == 0

    @pytest.mark.asyncio
    async def test_get_published_portfolio(self, portfolio_service, mock_supabase_client):
        """Test getting published portfolio with view count increment"""
        # Setup mock
        initial_view_count = 10
        mock_select = Mock()
        mock_select.data = [
            {
                "id": "portfolio-id",
                "username": "testuser",
                "profile_slug": "test-portfolio",
                "view_count": initial_view_count,
                "is_published": True,
                "published_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "profile_data": {
                    "user": {"name": "Test User", "github": {"username": "testuser", "avatar_url": "https://example.com/avatar.jpg"}},
                    "profile": {"name": "Test Portfolio", "description": "Test description"},
                    "projects": [],
                },
            }
        ]

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_select

        mock_update_query = Mock()
        mock_update_query.eq.return_value = mock_update_query
        mock_update_query.execute.return_value = Mock()

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_table.update.return_value = mock_update_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await portfolio_service.get_published_portfolio(
            mock_supabase_client, "testuser", "test-portfolio", increment_view_count=True
        )

        # Assert
        assert isinstance(result, PortfolioResponse)
        assert result.view_count == initial_view_count + 1
        assert result.username == "testuser"
        assert result.portfolio_slug == "test-portfolio"

    @pytest.mark.asyncio
    async def test_get_published_portfolio_no_increment(self, portfolio_service, mock_supabase_client):
        """Test getting published portfolio without incrementing view count"""
        # Setup mock
        initial_view_count = 10
        mock_select = Mock()
        mock_select.data = [
            {
                "id": "portfolio-id",
                "username": "testuser",
                "profile_slug": "test-portfolio",
                "view_count": initial_view_count,
                "is_published": True,
                "published_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "profile_data": {
                    "user": {"name": "Test User", "github": {"username": "testuser", "avatar_url": "https://example.com/avatar.jpg"}},
                    "profile": {"name": "Test Portfolio", "description": "Test description"},
                    "projects": [],
                },
            }
        ]

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_select

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await portfolio_service.get_published_portfolio(
            mock_supabase_client, "testuser", "test-portfolio", increment_view_count=False
        )

        # Assert
        assert isinstance(result, PortfolioResponse)
        assert result.view_count == initial_view_count  # Not incremented
        mock_table.update.assert_not_called()  # Update should not be called

    @pytest.mark.asyncio
    async def test_get_published_portfolio_not_found(self, portfolio_service, mock_supabase_client):
        """Test getting published portfolio that doesn't exist"""
        # Setup mock
        mock_select = Mock()
        mock_select.data = []

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_select

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_supabase_client.table.return_value = mock_table

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await portfolio_service.get_published_portfolio(mock_supabase_client, "testuser", "nonexistent")

        assert exc_info.value.status_code == 404
        assert "Portfolio not found" in exc_info.value.detail
