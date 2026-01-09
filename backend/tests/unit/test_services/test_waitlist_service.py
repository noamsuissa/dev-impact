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
        # Setup mocks - code does existing.data[0], so data must be a list
        mock_existing = Mock()
        mock_existing.data = []  # Empty list, not None - email not already in waitlist

        mock_existing_query = Mock()
        mock_existing_query.eq.return_value = mock_existing_query
        mock_existing_query.execute.return_value = mock_existing

        mock_insert = Mock()
        mock_insert.data = [
            {
                "id": "waitlist_123",
                "email": "newuser@example.com",
                "name": "New User",
                "created_at": "2024-01-01T00:00:00",
            }
        ]
        mock_insert_query = Mock()
        mock_insert_query.execute.return_value = mock_insert

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "waitlist":
                mock_table.select.return_value = mock_existing_query
                mock_table.insert.return_value = mock_insert_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        mock_email_client.send_email = AsyncMock()

        # Execute
        result = await waitlist_service.signup(mock_supabase_client, email="newuser@example.com", name="New User")

        # Assert
        assert result.success is True
        assert "added to waitlist" in result.message.lower() or "successfully" in result.message.lower()

        # Verify email was sent
        mock_email_client.send_email.assert_called_once()
        email_call = mock_email_client.send_email.call_args
        assert email_call[1]["to_email"] == "newuser@example.com"
        assert "waitlist" in email_call[1]["template_name"].lower()

    @pytest.mark.asyncio
    async def test_signup_existing_user(self, waitlist_service, mock_supabase_client, mock_email_client):
        """Test waitlist signup for user already in waitlist"""
        # Setup mock - email already exists
        # Code does existing.data[0], so data must be a list
        mock_existing = Mock()
        mock_existing.data = [
            {"email": "existing@example.com", "id": "waitlist_123", "name": "Existing User", "created_at": "2024-01-01T00:00:00"}
        ]  # List, not dict

        mock_existing_query = Mock()
        mock_existing_query.eq.return_value = mock_existing_query
        mock_existing_query.execute.return_value = mock_existing

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "waitlist":
                mock_table.select.return_value = mock_existing_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

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
        # Setup mocks - code does existing.data[0], so data must be a list
        mock_existing = Mock()
        mock_existing.data = []  # Empty list, not None

        mock_existing_query = Mock()
        mock_existing_query.eq.return_value = mock_existing_query
        mock_existing_query.execute.return_value = mock_existing

        mock_insert = Mock()
        mock_insert.data = [
            {
                "id": "waitlist_456",
                "email": "test@example.com",
                "name": "Test User",
                "created_at": "2024-01-01T00:00:00",
            }
        ]
        mock_insert_query = Mock()
        mock_insert_query.execute.return_value = mock_insert

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "waitlist":
                mock_table.select.return_value = mock_existing_query
                mock_table.insert.return_value = mock_insert_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Mock email sending to fail - EmailClient returns False, not raises exception
        mock_email_client.send_email = AsyncMock(return_value=False)

        # Execute - should still succeed even if email fails
        result = await waitlist_service.signup(mock_supabase_client, email="test@example.com", name="Test User")

        # Assert - signup succeeds even with email failure
        assert result.success is True
        assert "added to waitlist" in result.message.lower()

    @pytest.mark.asyncio
    async def test_signup_database_error(self, waitlist_service, mock_supabase_client):
        """Test waitlist signup handles database errors"""
        # Setup mock to raise error
        mock_existing_query = Mock()
        mock_existing_query.eq.return_value = mock_existing_query
        mock_existing_query.execute.side_effect = Exception("Database error")

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "waitlist":
                mock_table.select.return_value = mock_existing_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await waitlist_service.signup(mock_supabase_client, email="error@example.com", name="Error User")

        assert exc_info.value.status_code == 500
        assert "Failed to add to waitlist" in exc_info.value.detail
