"""
Unit tests for GitHubClient integration
Tests GitHub OAuth Device Flow with mocked HTTP calls
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from backend.integrations.github_client import GitHubClient
from backend.schemas.github_auth import DeviceCodeResponse, GitHubUser, TokenResponse


class TestGitHubClient:
    """Test suite for GitHubClient"""

    def test_initialization(self, github_config):
        """Test GitHub client initializes with config"""
        client = GitHubClient(github_config)

        assert client.config == github_config
        assert client.config.client_id == "test_client_id"

    @pytest.mark.asyncio
    async def test_initiate_device_flow(self, github_config):
        """Test initiating GitHub device flow"""
        # Mock httpx
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.json.return_value = {
                "device_code": "device_code_123",
                "user_code": "ABCD-1234",
                "verification_uri": "https://github.com/login/device",
                "expires_in": 900,
                "interval": 5,
            }
            mock_response.raise_for_status = Mock()
            mock_client.post.return_value = mock_response

            client = GitHubClient(github_config)

            # Execute
            result = await client.initiate_device_flow()

            # Assert
            assert isinstance(result, DeviceCodeResponse)
            assert result.device_code == "device_code_123"
            assert result.user_code == "ABCD-1234"
            assert result.verification_uri == "https://github.com/login/device"

    @pytest.mark.asyncio
    async def test_poll_for_token_success(self, github_config):
        """Test successful token retrieval"""
        # Mock httpx
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.json.return_value = {"access_token": "gho_token_123", "token_type": "bearer", "scope": "read:user"}
            mock_client.post.return_value = mock_response

            client = GitHubClient(github_config)

            # Execute
            result = await client.poll_for_token("device_code_123")

            # Assert
            assert isinstance(result, TokenResponse)
            assert result.status == "success"
            assert result.access_token == "gho_token_123"
            assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_poll_for_token_pending(self, github_config):
        """Test polling when authorization is still pending"""
        # Mock httpx
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.json.return_value = {"error": "authorization_pending"}
            mock_client.post.return_value = mock_response

            client = GitHubClient(github_config)

            # Execute
            result = await client.poll_for_token("device_code_123")

            # Assert - should return None when pending
            assert result is None

    @pytest.mark.asyncio
    async def test_poll_for_token_expired(self, github_config):
        """Test polling when device code expired"""
        # Mock httpx
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.json.return_value = {"error": "expired_token"}
            mock_client.post.return_value = mock_response

            client = GitHubClient(github_config)

            # Execute and expect exception
            with pytest.raises(HTTPException) as exc_info:
                await client.poll_for_token("expired_device_code")

            assert exc_info.value.status_code == 400  # Correct status code for expired token
            assert "Device code expired" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_user_profile(self, github_config):
        """Test fetching GitHub user profile"""
        # Mock httpx
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.json.return_value = {
                "login": "testuser",
                "avatar_url": "https://github.com/avatar.jpg",
                "name": "Test User",
                "email": "test@example.com",
            }
            mock_response.raise_for_status = Mock()
            mock_client.get.return_value = mock_response

            client = GitHubClient(github_config)

            # Execute
            result = await client.get_user_profile("gho_token_123")

            # Assert
            assert isinstance(result, GitHubUser)
            assert result.login == "testuser"
            assert result.avatar_url == "https://github.com/avatar.jpg"
            assert result.name == "Test User"
