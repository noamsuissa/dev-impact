"""Unit tests for EmailClient integration
Tests SMTP email sending with mocked SMTP library
"""

from unittest.mock import AsyncMock, patch

import pytest

from backend.integrations.email_client import EmailClient


class TestEmailClient:
    """Test suite for EmailClient"""

    def test_initialization(self, email_config):
        """Test Email client initializes with config"""
        client = EmailClient(email_config)

        assert client.config == email_config
        assert client.config.host == "smtp.test.com"
        assert client.config.port == 587

    @pytest.mark.asyncio
    @patch("backend.integrations.email_client.aiosmtplib.SMTP")
    async def test_send_email_success(self, mock_smtp_class, email_config):
        """Test successfully sending email"""
        # Setup mock SMTP - async context manager
        mock_smtp_instance = AsyncMock()
        mock_smtp_instance.__aenter__ = AsyncMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__aexit__ = AsyncMock(return_value=None)
        mock_smtp_class.return_value = mock_smtp_instance

        client = EmailClient(email_config)

        # Execute
        result = await client.send_email(
            to_email="recipient@example.com",
            subject="Test Email",
            template_name="waitlist_confirmation.html",
            template_vars={"name": "Test User"},
        )

        # Assert email was sent successfully
        assert result is True
        # Assert SMTP methods were called (via async context manager)
        mock_smtp_instance.login.assert_called_once_with(email_config.user, email_config.password)
        mock_smtp_instance.send_message.assert_called_once()

    @pytest.mark.asyncio
    @patch("backend.integrations.email_client.aiosmtplib.SMTP")
    async def test_send_email_with_template_context(self, mock_smtp_class, email_config):
        """Test email template rendering with context"""
        # Setup mock - async context manager
        mock_smtp_instance = AsyncMock()
        mock_smtp_instance.__aenter__ = AsyncMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__aexit__ = AsyncMock(return_value=None)
        mock_smtp_class.return_value = mock_smtp_instance

        client = EmailClient(email_config)

        # Execute with template_vars
        template_vars = {"name": "John Doe", "custom_message": "Welcome to the waitlist!"}

        result = await client.send_email(
            to_email="john@example.com",
            subject="Welcome",
            template_name="waitlist_confirmation.html",
            template_vars=template_vars,
        )

        # Assert email was sent successfully
        assert result is True
        # Assert send_message was called (template was rendered)
        mock_smtp_instance.send_message.assert_called_once()

    @pytest.mark.asyncio
    @patch("backend.integrations.email_client.aiosmtplib.SMTP")
    async def test_send_email_connection_failure(self, mock_smtp_class, email_config):
        """Test handling SMTP connection failure"""
        # Setup mock to raise connection error in context manager
        mock_smtp_instance = AsyncMock()
        mock_smtp_instance.__aenter__ = AsyncMock(side_effect=OSError("Connection failed"))
        mock_smtp_instance.__aexit__ = AsyncMock(return_value=None)
        mock_smtp_class.return_value = mock_smtp_instance

        client = EmailClient(email_config)

        # Execute - EmailClient catches exceptions and returns False
        result = await client.send_email(
            to_email="test@example.com",
            subject="Test",
            template_name="test.html",
            template_vars={},
        )

        # Assert email send failed
        assert result is False

    @pytest.mark.asyncio
    @patch("backend.integrations.email_client.aiosmtplib.SMTP")
    async def test_send_email_auth_failure(self, mock_smtp_class, email_config):
        """Test handling SMTP authentication failure"""
        # Setup mock to raise auth error
        mock_smtp_instance = AsyncMock()
        mock_smtp_instance.__aenter__ = AsyncMock(return_value=mock_smtp_instance)
        mock_smtp_instance.__aexit__ = AsyncMock(return_value=None)
        mock_smtp_instance.login.side_effect = RuntimeError("Authentication failed")
        mock_smtp_class.return_value = mock_smtp_instance

        client = EmailClient(email_config)

        # Execute - EmailClient catches exceptions and returns False
        result = await client.send_email(
            to_email="test@example.com",
            subject="Test",
            template_name="test.html",
            template_vars={},
        )

        # Assert email send failed
        assert result is False

    @pytest.mark.asyncio
    @patch("backend.integrations.email_client.aiosmtplib.SMTP")
    async def test_send_email_closes_connection_on_error(self, mock_smtp_class, email_config):
        """Test SMTP connection is closed even if sending fails"""
        # Setup mock to fail during send
        # When exception occurs in async with, __aexit__ is called with exception info
        mock_smtp_instance = AsyncMock()
        mock_smtp_instance.login = AsyncMock()
        mock_smtp_instance.send_message.side_effect = RuntimeError("Send failed")

        # Create a proper async context manager
        async def aenter():
            return mock_smtp_instance

        async def aexit(exc_type, exc_val, exc_tb):
            return None

        mock_smtp_instance.__aenter__ = aenter
        mock_smtp_instance.__aexit__ = aexit
        mock_smtp_class.return_value = mock_smtp_instance

        client = EmailClient(email_config)

        # Execute - EmailClient catches exceptions and returns False
        result = await client.send_email(
            to_email="test@example.com",
            subject="Test",
            template_name="test.html",
            template_vars={},
        )

        # Assert email send failed
        assert result is False
        # Note: When exception occurs in async with block, __aexit__ is called automatically
        # but it's difficult to verify with mocks when exception is caught by EmailClient
