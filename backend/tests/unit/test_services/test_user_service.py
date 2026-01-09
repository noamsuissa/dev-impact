"""Unit tests for UserService
Tests business logic with mocked dependencies
"""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from backend.schemas.user import UserProfile
from backend.services.user_service import UserService


class TestUserService:
    """Test suite for UserService"""

    def test_initialization(self, mock_stripe_client):
        """Test UserService initializes with injected dependencies"""
        service = UserService(stripe_client=mock_stripe_client)

        assert service.stripe_client == mock_stripe_client

    @pytest.mark.asyncio
    async def test_get_profile_success(self, user_service, mock_supabase_client):
        """Test getting user profile successfully"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = Mock(
            data={
                "id": "user_123",
                "username": "testuser",
                "full_name": "Test User",
                "github_username": "testgh",
                "github_avatar_url": "https://github.com/avatar.jpg",
                "city": "New York",
                "country": "USA",
                "is_published": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        )

        # Execute
        result = await user_service.get_profile(mock_supabase_client, "user_123")

        # Assert
        assert isinstance(result, UserProfile)
        assert result.id == "user_123"
        assert result.username == "testuser"
        assert result.full_name == "Test User"

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self, user_service, mock_supabase_client):
        """Test getting profile that doesn't exist"""
        # Setup mock - no profile found
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = Mock(
            data=None
        )

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await user_service.get_profile(mock_supabase_client, "nonexistent_user")

        assert exc_info.value.status_code == 404
        assert "Profile not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_profile(self, user_service, mock_supabase_client):
        """Test updating user profile"""
        # Setup mock
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock(
            data=[
                {
                    "id": "user_123",
                    "username": "updateduser",
                    "full_name": "Updated Name",
                    "github_username": None,
                    "github_avatar_url": None,
                    "city": "San Francisco",
                    "country": "USA",
                    "is_published": True,
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-02T00:00:00",
                }
            ]
        )

        # Execute
        update_data = {
            "full_name": "Updated Name",
            "city": "San Francisco",
            "is_published": True,
        }
        result = await user_service.update_profile(mock_supabase_client, "user_123", update_data)

        # Assert
        assert isinstance(result, UserProfile)
        assert result.full_name == "Updated Name"
        assert result.city == "San Francisco"
        assert result.is_published is True

    @pytest.mark.asyncio
    async def test_delete_account(self, user_service, mock_supabase_client, mock_stripe_client):
        """Test deleting user account cancels subscription"""
        # Setup mocks
        mock_stripe_client.cancel_subscription = AsyncMock()
        mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = Mock()
        mock_supabase_client.auth.admin.delete_user = Mock()

        # Execute
        result = await user_service.delete_account(mock_supabase_client, "user_123")

        # Assert
        assert result.success is True
        assert "deleted successfully" in result.message

        # Verify Stripe cancellation was called
        mock_stripe_client.cancel_subscription.assert_called_once_with(mock_supabase_client, "user_123")

        # Verify database deletion was called
        mock_supabase_client.table.assert_called()
        mock_supabase_client.auth.admin.delete_user.assert_called_once_with("user_123")

    @pytest.mark.asyncio
    async def test_delete_account_no_subscription(self, user_service, mock_supabase_client, mock_stripe_client):
        """Test deleting account when user has no subscription"""
        # Setup mocks - Stripe cancellation raises exception
        mock_stripe_client.cancel_subscription = AsyncMock(side_effect=Exception("No subscription"))
        mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = Mock()
        mock_supabase_client.auth.admin.delete_user = Mock()

        # Execute - should still succeed
        result = await user_service.delete_account(mock_supabase_client, "user_123")

        # Assert
        assert result.success is True
        # Account deletion should continue even if subscription cancellation fails

    def test_validate_username_valid(self, user_service):
        """Test username validation with valid usernames"""
        assert user_service.validate_username("validuser") is True
        assert user_service.validate_username("user-123") is True
        assert user_service.validate_username("my-username") is True

    def test_validate_username_invalid(self, user_service):
        """Test username validation with invalid usernames"""
        assert user_service.validate_username("") is False  # Empty
        assert user_service.validate_username("ab") is False  # Too short
        assert user_service.validate_username("a" * 51) is False  # Too long
        assert user_service.validate_username("User Name") is False  # Spaces
        assert user_service.validate_username("USER") is False  # Uppercase
        assert user_service.validate_username("user@name") is False  # Special chars

    @pytest.mark.asyncio
    async def test_check_username_available(self, user_service, mock_supabase_client):
        """Test checking username availability"""
        # Setup mock - username is available
        mock_supabase_client.rpc.return_value.execute.return_value = Mock(data=True)

        # Execute
        result = await user_service.check_username(mock_supabase_client, "availableuser")

        # Assert
        assert result.available is True
        assert result.valid is True
        assert "available" in result.message.lower()

    @pytest.mark.asyncio
    async def test_check_username_taken(self, user_service, mock_supabase_client):
        """Test checking username that's taken"""
        # Setup mock - username is not available
        mock_supabase_client.rpc.return_value.execute.return_value = Mock(data=False)

        # Execute
        result = await user_service.check_username(mock_supabase_client, "takenuser")

        # Assert
        assert result.available is False
        assert result.valid is True
        assert "taken" in result.message.lower()

    @pytest.mark.asyncio
    async def test_check_username_invalid_format(self, user_service, mock_supabase_client):
        """Test checking username with invalid format"""
        # Execute
        result = await user_service.check_username(mock_supabase_client, "INVALID USERNAME")

        # Assert
        assert result.available is False
        assert result.valid is False
        assert "3-50 characters" in result.message
