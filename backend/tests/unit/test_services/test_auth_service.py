"""
Unit tests for AuthService
Tests business logic with mocked dependencies
"""

from unittest.mock import AsyncMock, Mock, patch

import jwt
import pytest
from fastapi import HTTPException

from backend.schemas.auth import AuthResponse, MessageResponse
from backend.services.auth.auth_service import AuthService


class TestAuthService:
    """Test suite for AuthService"""

    def test_initialization(self):
        """Test AuthService initializes correctly"""
        service = AuthService()
        assert service is not None

    @pytest.mark.asyncio
    async def test_sign_up_success(self, auth_service, mock_supabase_client):
        """Test successful user registration"""
        # Setup mock
        mock_user = Mock()
        mock_user.id = "user_123"
        mock_user.email = "test@example.com"
        mock_user.created_at = "2024-01-01T00:00:00"

        mock_session = Mock()
        mock_session.access_token = "access_token_123"
        mock_session.refresh_token = "refresh_token_123"
        mock_session.expires_at = 1704067200

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase_client.auth.sign_up = Mock(return_value=mock_auth_response)

        # Execute
        result = await auth_service.sign_up(mock_supabase_client, "test@example.com", "password123")

        # Assert
        assert isinstance(result, AuthResponse)
        assert result.user.id == "user_123"
        assert result.session is not None
        assert result.requires_email_verification is False

    @pytest.mark.asyncio
    async def test_sign_up_email_exists(self, auth_service, mock_supabase_client):
        """Test sign up with existing email"""
        # Setup mock - no user returned
        mock_auth_response = Mock()
        mock_auth_response.user = None

        mock_supabase_client.auth.sign_up = Mock(return_value=mock_auth_response)

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.sign_up(mock_supabase_client, "existing@example.com", "password123")

        assert exc_info.value.status_code == 400
        assert "Failed to create account" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_sign_in_success(self, auth_service, mock_supabase_client):
        """Test successful login without MFA"""
        # Setup mock
        mock_user = Mock()
        mock_user.id = "user_123"
        mock_user.email = "test@example.com"
        mock_user.created_at = "2024-01-01T00:00:00"

        mock_session = Mock()
        mock_session.access_token = "access_token_123"
        mock_session.refresh_token = "refresh_token_123"
        mock_session.expires_at = 1704067200

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase_client.auth.sign_in_with_password = Mock(return_value=mock_auth_response)

        # Mock MFA check - no factors
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_client.get.return_value = mock_response

            # Execute
            result = await auth_service.sign_in(mock_supabase_client, "test@example.com", "password123")

            # Assert
            assert isinstance(result, AuthResponse)
            assert result.user.id == "user_123"
            assert result.session is not None
            assert result.requires_mfa is False

    @pytest.mark.asyncio
    async def test_sign_in_with_mfa(self, auth_service, mock_supabase_client):
        """Test login with MFA challenge"""
        # Setup mock - password sign in succeeds
        mock_user = Mock()
        mock_user.id = "user_123"
        mock_user.email = "test@example.com"
        mock_user.created_at = "2024-01-01T00:00:00"

        mock_session = Mock()
        mock_session.access_token = "access_token_123"
        mock_session.refresh_token = "refresh_token_123"
        mock_session.expires_at = 1704067200

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase_client.auth.sign_in_with_password = Mock(return_value=mock_auth_response)

        # Mock MFA check - has factors
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock factors list
            mock_factors_response = Mock()
            mock_factors_response.status_code = 200
            mock_factors_response.json.return_value = [{"id": "factor_123", "factor_type": "totp", "status": "verified"}]
            mock_client.get.return_value = mock_factors_response

            # Mock challenge creation
            mock_challenge_response = Mock()
            mock_challenge_response.status_code = 200
            mock_challenge_response.json.return_value = {"id": "challenge_123"}
            mock_client.post.return_value = mock_challenge_response

            # Execute
            result = await auth_service.sign_in(mock_supabase_client, "test@example.com", "password123")

            # Assert
            assert isinstance(result, AuthResponse)
            assert result.requires_mfa is True
            assert result.mfa_challenge_id == "challenge_123"
            assert result.session is None  # No session until MFA verified

    @pytest.mark.asyncio
    async def test_sign_in_invalid_credentials(self, auth_service, mock_supabase_client):
        """Test login with wrong password"""
        # Setup mock - no user/session returned
        mock_auth_response = Mock()
        mock_auth_response.user = None
        mock_auth_response.session = None

        mock_supabase_client.auth.sign_in_with_password = Mock(return_value=mock_auth_response)

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.sign_in(mock_supabase_client, "test@example.com", "wrongpassword")

        assert exc_info.value.status_code == 401
        assert "Invalid email or password" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_sign_out(self, auth_service, mock_supabase_client):
        """Test signing out user"""
        # Setup mock
        mock_supabase_client.postgrest.auth = Mock()
        mock_supabase_client.auth.sign_out = Mock()

        # Execute
        result = await auth_service.sign_out(mock_supabase_client, "access_token_123")

        # Assert
        assert isinstance(result, MessageResponse)
        assert result.success is True
        mock_supabase_client.postgrest.auth.assert_called_once_with("access_token_123")
        mock_supabase_client.auth.sign_out.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_email(self, auth_service, mock_supabase_client):
        """Test sending password reset email"""
        # Setup mock
        mock_supabase_client.auth.reset_password_email = Mock()

        # Execute
        result = await auth_service.reset_password_email(mock_supabase_client, "test@example.com")

        # Assert
        assert isinstance(result, MessageResponse)
        assert result.success is True
        mock_supabase_client.auth.reset_password_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_password(self, auth_service):
        """Test updating password from token"""
        # Create a valid JWT token
        token_payload = {"sub": "user_123", "exp": 9999999999}
        access_token = jwt.encode(token_payload, "secret", algorithm="HS256")

        # Mock httpx for Admin API call
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.put.return_value = mock_response

            # Execute
            result = await auth_service.update_password(access_token, "newpassword123")

            # Assert
            assert isinstance(result, MessageResponse)
            assert result.success is True
            assert "updated successfully" in result.message.lower()

    @pytest.mark.asyncio
    async def test_update_password_invalid_token(self, auth_service):
        """Test updating password with invalid token"""
        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.update_password("invalid_token", "newpassword123")

        assert exc_info.value.status_code in [400, 500]
