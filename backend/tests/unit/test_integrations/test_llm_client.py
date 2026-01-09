"""
Unit tests for LLMClient integration
Tests LLM completion generation with mocked LiteLLM calls
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from litellm.exceptions import APIError, AuthenticationError, RateLimitError

from backend.integrations.llm_client import LLMClient


class TestLLMClient:
    """Test suite for LLMClient"""

    def test_initialization(self, llm_config):
        """Test LLM client initializes with config"""
        client = LLMClient(llm_config)

        assert client.config == llm_config
        assert client.config.openrouter_api_key == "sk_test_openrouter"

    @pytest.mark.asyncio
    @patch("backend.integrations.llm_client.acompletion")
    async def test_generate_completion_openrouter(self, mock_acompletion, llm_config):
        """Test generating completion with OpenRouter"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test completion"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "openrouter/anthropic/claude-3-opus"
        mock_response.usage = MagicMock()
        mock_response.usage.model_dump.return_value = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}

        mock_acompletion.return_value = mock_response

        client = LLMClient(llm_config)

        # Execute
        result = await client.generate_completion(provider="openrouter", messages=[{"role": "user", "content": "Hello"}])

        # Assert
        assert result["content"] == "Test completion"
        assert result["model"] == "openrouter/anthropic/claude-3-opus"
        assert result["finish_reason"] == "stop"
        assert result["usage"] is not None

        # Verify correct model prefix was used
        call_kwargs = mock_acompletion.call_args[1]
        assert call_kwargs["model"].startswith("openrouter/")

    @pytest.mark.asyncio
    @patch("backend.integrations.llm_client.acompletion")
    async def test_generate_completion_groq(self, mock_acompletion, llm_config):
        """Test generating completion with Groq"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Groq completion"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "groq/llama-3.1-8b-instant"
        mock_response.usage = MagicMock()
        mock_response.usage.model_dump.return_value = {"prompt_tokens": 5, "completion_tokens": 15, "total_tokens": 20}

        mock_acompletion.return_value = mock_response

        client = LLMClient(llm_config)

        # Execute
        result = await client.generate_completion(provider="groq", messages=[{"role": "user", "content": "Hello"}])

        # Assert
        assert result["content"] == "Groq completion"
        assert result["model"].startswith("groq/")

        # Verify correct model prefix was used
        call_kwargs = mock_acompletion.call_args[1]
        assert call_kwargs["model"].startswith("groq/")

    @pytest.mark.asyncio
    @patch("backend.integrations.llm_client.acompletion")
    async def test_generate_completion_rate_limit(self, mock_acompletion, llm_config):
        """Test handling rate limit errors"""
        # Setup mock to raise RateLimitError
        # LiteLLM exceptions require llm_provider and model parameters
        mock_acompletion.side_effect = RateLimitError(
            message="Rate limit exceeded",
            llm_provider="openrouter",
            model="test-model",
        )

        client = LLMClient(llm_config)

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await client.generate_completion(provider="openrouter", messages=[{"role": "user", "content": "Hello"}])

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("backend.integrations.llm_client.acompletion")
    async def test_generate_completion_authentication_error(self, mock_acompletion, llm_config):
        """Test handling authentication errors"""
        # Setup mock to raise AuthenticationError
        # LiteLLM exceptions require llm_provider and model parameters
        mock_acompletion.side_effect = AuthenticationError(
            message="Invalid API key",
            llm_provider="openrouter",
            model="test-model",
        )

        client = LLMClient(llm_config)

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await client.generate_completion(provider="openrouter", messages=[{"role": "user", "content": "Hello"}])

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("backend.integrations.llm_client.acompletion")
    async def test_generate_completion_api_error(self, mock_acompletion, llm_config):
        """Test handling API errors"""
        # Setup mock to raise APIError
        # APIError requires status_code, llm_provider, and model parameters
        mock_acompletion.side_effect = APIError(
            message="API error",
            status_code=502,
            llm_provider="openrouter",
            model="test-model",
        )

        client = LLMClient(llm_config)

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await client.generate_completion(provider="openrouter", messages=[{"role": "user", "content": "Hello"}])

        assert exc_info.value.status_code == 502
        assert "API error" in exc_info.value.detail

    def test_get_available_models(self, llm_config):
        """Test getting available models"""
        client = LLMClient(llm_config)

        # Execute
        result = client.get_available_models()

        # Assert
        assert isinstance(result, dict)
        assert "openrouter" in result
        assert "groq" in result
        assert len(result["openrouter"]) > 0
        assert len(result["groq"]) > 0

    def test_get_providers_status(self, llm_config):
        """Test getting provider configuration status"""
        client = LLMClient(llm_config)

        # Execute
        result = client.get_providers_status()

        # Assert
        assert isinstance(result, dict)
        assert "openrouter" in result
        assert "groq" in result
        assert result["openrouter"]["configured"] is True
        assert result["groq"]["configured"] is True
        assert result["openrouter"]["default_model"] == "test-model"
        assert result["groq"]["default_model"] == "test-groq-model"
