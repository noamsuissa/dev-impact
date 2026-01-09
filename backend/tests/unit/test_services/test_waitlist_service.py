"""Unit tests for WaitlistService
Tests waitlist signup with mocked email client
"""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from backend.services.waitlist_service import WaitlistService


class TestWaitlistService:
    """Test suite for WaitlistService"""

    def test_initialization(self, mock_email_client):
        """Test WaitlistService initializes with injected email client"""
        service = WaitlistService(email_client=mock_email_client)

        assert service.email_client == mock_email_client

    @pytest.mark.asyncio
    async def test_signup_new_user(self, waitlist_service, mock_supabase_client, mock_email_client):
        """Test successful waitlist signup for new user"""
        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = Mock(
            data=None  # Email not already in waitlist
        )

        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[
                {
                    "id": "waitlist_123",
                    "email": "newuser@example.com",
                    "name": "New User",
                    "created_at": "2024-01-01T00:00:00",
                }
            ]
        )

        mock_email_client.send_email = AsyncMock()

        # Execute
        result = await waitlist_service.signup(mock_supabase_client, email="newuser@example.com", name="New User")

        # Assert
        assert result.success is True
        assert "added to the waitlist" in result.message

        # Verify email was sent
        mock_email_client.send_email.assert_called_once()
        email_call = mock_email_client.send_email.call_args
        assert email_call[1]["to_email"] == "newuser@example.com"
        assert "waitlist" in email_call[1]["template_name"].lower()

    @pytest.mark.asyncio
    async def test_signup_existing_user(self, waitlist_service, mock_supabase_client, mock_email_client):
        """Test waitlist signup for user already in waitlist"""
        # Setup mock - email already exists
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = Mock(
            data={"email": "existing@example.com"}
        )

        mock_email_client.send_email = AsyncMock()

        # Execute
        result = await waitlist_service.signup(mock_supabase_client, email="existing@example.com", name="Existing User")

        # Assert
        assert result.success is True
        assert "already on" in result.message.lower()

        # Verify no email was sent
        mock_email_client.send_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_signup_email_failure(self, waitlist_service, mock_supabase_client, mock_email_client):
        """Test waitlist signup succeeds even if email fails"""
        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = Mock(
            data=None
        )

        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[
                {
                    "id": "waitlist_456",
                    "email": "test@example.com",
                    "name": "Test User",
                    "created_at": "2024-01-01T00:00:00",
                }
            ]
        )

        # Mock email sending to fail
        mock_email_client.send_email = AsyncMock(side_effect=Exception("SMTP error"))

        # Execute - should still succeed
        result = await waitlist_service.signup(mock_supabase_client, email="test@example.com", name="Test User")

        # Assert - signup succeeds even with email failure
        assert result.success is True

    @pytest.mark.asyncio
    async def test_signup_database_error(self, waitlist_service, mock_supabase_client):
        """Test waitlist signup handles database errors"""
        # Setup mock to raise error
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.side_effect = (
            Exception("Database error")
        )

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await waitlist_service.signup(mock_supabase_client, email="error@example.com", name="Error User")

        assert exc_info.value.status_code == 500
        assert "Failed to sign up for waitlist" in exc_info.value.detail
