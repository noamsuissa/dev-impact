"""
Unit tests for MFAService
Tests business logic with mocked dependencies
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from backend.schemas.auth import MessageResponse, MFAEnrollResponse, MFAListResponse
from backend.services.auth.mfa_service import MFAService


class TestMFAService:
    """Test suite for MFAService"""

    def test_initialization(self):
        """Test MFAService initializes correctly"""
        service = MFAService()
        assert service is not None

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_anon_key"})
    async def test_mfa_enroll(self, mfa_service):
        """Test enrolling in MFA (TOTP)"""
        # Mock httpx for Supabase Auth API
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "factor_123",
                "type": "totp",
                "totp": {"qr_code": "data:image/png;base64,test", "secret": "JBSWY3DPEHPK3PXP"},
                "friendly_name": "Authenticator App",
            }
            mock_client.post.return_value = mock_response

            # Execute
            result = await mfa_service.mfa_enroll("access_token_123", "My Authenticator")

            # Assert
            assert isinstance(result, MFAEnrollResponse)
            assert result.id == "factor_123"
            assert result.type == "totp"
            assert result.qr_code is not None
            assert result.secret is not None

    @pytest.mark.asyncio
    async def test_mfa_enroll_missing_config(self, mfa_service):
        """Test MFA enrollment with missing configuration"""
        # Mock environment to return None
        with patch("os.getenv", return_value=None):
            # Execute and expect exception
            with pytest.raises(HTTPException) as exc_info:
                await mfa_service.mfa_enroll("access_token_123", "My Authenticator")

            assert exc_info.value.status_code == 500
            assert "configuration not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_anon_key"})
    async def test_mfa_verify_enrollment(self, mfa_service):
        """Test verifying MFA enrollment with code"""
        # Mock httpx for Supabase Auth API
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock challenge creation
            mock_challenge_response = Mock()
            mock_challenge_response.status_code = 200
            mock_challenge_response.json.return_value = {"id": "challenge_123"}
            mock_client.post.return_value = mock_challenge_response

            # Mock verification
            mock_verify_response = Mock()
            mock_verify_response.status_code = 200
            mock_client.post.side_effect = [mock_challenge_response, mock_verify_response]

            # Execute
            result = await mfa_service.mfa_verify_enrollment("access_token_123", "factor_123", "123456")

            # Assert
            assert isinstance(result, MessageResponse)
            assert result.success is True
            assert "verified" in result.message.lower()

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_anon_key"})
    async def test_mfa_verify_enrollment_invalid_code(self, mfa_service):
        """Test MFA verification with invalid code"""
        # Mock httpx for Supabase Auth API
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock challenge creation
            mock_challenge_response = Mock()
            mock_challenge_response.status_code = 200
            mock_challenge_response.json.return_value = {"id": "challenge_123"}
            mock_client.post.return_value = mock_challenge_response

            # Mock verification failure
            mock_verify_response = Mock()
            mock_verify_response.status_code = 400
            mock_verify_response.text = "Invalid code"
            mock_client.post.side_effect = [mock_challenge_response, mock_verify_response]

            # Execute and expect exception
            with pytest.raises(HTTPException) as exc_info:
                await mfa_service.mfa_verify_enrollment("access_token_123", "factor_123", "wrong_code")

            assert exc_info.value.status_code == 400
            assert "Invalid verification code" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_SERVICE_ROLE_KEY": "test_service_key"})
    async def test_mfa_list_factors(self, mfa_service):
        """Test listing user's MFA factors"""
        # Mock httpx for Admin API
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"id": "factor_123", "factor_type": "totp", "friendly_name": "My Authenticator", "status": "verified"}
            ]
            mock_client.get.return_value = mock_response

            # Execute
            result = await mfa_service.mfa_list_factors("user_123")

            # Assert
            assert isinstance(result, MFAListResponse)
            assert len(result.factors) == 1
            assert result.factors[0].id == "factor_123"
            assert result.factors[0].type == "totp"

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_SERVICE_ROLE_KEY": "test_service_key"})
    async def test_mfa_list_factors_empty(self, mfa_service):
        """Test listing factors when user has none"""
        # Mock httpx for Admin API
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 404
            mock_client.get.return_value = mock_response

            # Execute
            result = await mfa_service.mfa_list_factors("user_123")

            # Assert
            assert isinstance(result, MFAListResponse)
            assert len(result.factors) == 0

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_SERVICE_ROLE_KEY": "test_service_key"})
    async def test_mfa_unenroll(self, mfa_service):
        """Test removing MFA factor"""
        # Mock httpx for Admin API
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 204
            mock_client.delete.return_value = mock_response

            # Execute
            result = await mfa_service.mfa_unenroll("user_123", "factor_123")

            # Assert
            assert isinstance(result, MessageResponse)
            assert result.success is True
            assert "removed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_mfa_unenroll_missing_user_id(self, mfa_service):
        """Test unenrolling with missing user ID"""
        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await mfa_service.mfa_unenroll(None, "factor_123")

        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in exc_info.value.detail
