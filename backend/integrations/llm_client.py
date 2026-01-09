"""LLM integration client.
Unified interface for LLM providers through LiteLLM.
"""

import logging
import os
from typing import Any

from fastapi import HTTPException
from litellm import acompletion, completion
from litellm.exceptions import APIError, AuthenticationError, RateLimitError

from backend.core.config import LLMConfig

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with LLMs through LiteLLM."""

    def __init__(self, config: LLMConfig):
        """Initialize LLM client with configuration.

        Args:
        ----
            config: LLM configuration object

        """
        self.config = config

        # Set environment variables for LiteLLM
        # LiteLLM reads API keys from environment variables
        if self.config.openrouter_api_key:
            os.environ["OPENROUTER_API_KEY"] = self.config.openrouter_api_key
        if self.config.groq_api_key:
            os.environ["GROQ_API_KEY"] = self.config.groq_api_key

    def _get_completion_params(self, provider: str, model: str | None = None) -> dict[str, Any]:
        """Get provider-specific completion parameters.

        Args:
        ----
            provider: The LLM provider ('openrouter' or 'groq')
            model: Optional specific model name, otherwise uses default

        Returns:
        -------
            Dict of parameters for litellm completion call

        Raises:
        ------
            HTTPException: If provider is not supported or API key missing

        """
        if provider == "openrouter":
            if not self.config.openrouter_api_key:
                raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

            model_name = model or self.config.openrouter_model

            return {"model": f"openrouter/{model_name}"}

        elif provider == "groq":
            if not self.config.groq_api_key:
                raise HTTPException(status_code=500, detail="Groq API key not configured")

            model_name = model or self.config.groq_model

            return {"model": f"groq/{model_name}"}

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    async def generate_completion(
        self,
        provider: str,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        user_id: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate a completion using the specified provider through LiteLLM.

        Args:
        ----
            provider: LLM provider ('openrouter' or 'groq')
            messages: List of message dictionaries with 'role' and 'content'
            model: Optional model name, uses default if not provided
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            user_id: User ID for observability
            **kwargs: Additional parameters to pass to the model

        Returns:
        -------
            Completion response dict with 'content', 'usage', 'model', 'finish_reason'

        Raises:
        ------
            HTTPException: For configuration errors, API errors, rate limits, etc.

        """
        try:
            params = self._get_completion_params(provider, model)

            completion_params = {
                **params,
                "messages": messages,
                "temperature": temperature,
                "user": user_id,
            }

            if max_tokens:
                completion_params["max_tokens"] = max_tokens

            # Merge additional kwargs but don't override core params
            for key, value in kwargs.items():
                if key not in completion_params:
                    completion_params[key] = value

            response: Any = await acompletion(**completion_params)

            logger.info("LLM completion successful for provider: %s", provider)

            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump() if response.usage else None,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }

        except HTTPException:
            raise
        except AuthenticationError as e:
            logger.error("Authentication error for %s: %s", provider, e)
            raise HTTPException(status_code=401, detail=f"Invalid API key for {provider}") from e
        except RateLimitError as e:
            logger.error("Rate limit exceeded for %s: %s", provider, e)
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded for {provider}") from e
        except APIError as e:
            logger.error("API error for %s: %s", provider, e)
            raise HTTPException(status_code=502, detail=f"API error from {provider}") from e
        except Exception as e:
            logger.error("Unexpected error in LLM completion for %s: %s", provider, e)
            raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

    def generate_completion_sync(
        self,
        provider: str,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Synchronous version of generate_completion.

        Args:
        ----
            provider: LLM provider ('openrouter' or 'groq')
            messages: List of message dictionaries with 'role' and 'content'
            model: Optional model name, uses default if not provided
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the model

        Returns:
        -------
            Completion response dict with 'content', 'usage', 'model', 'finish_reason'

        Raises:
        ------
            HTTPException: For configuration errors, API errors, rate limits, etc.

        """
        try:
            params = self._get_completion_params(provider, model)

            completion_params = {
                **params,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens:
                completion_params["max_tokens"] = max_tokens

            # Merge additional kwargs but don't override core params
            for key, value in kwargs.items():
                if key not in completion_params:
                    completion_params[key] = value

            response: Any = completion(**completion_params)

            logger.info("LLM completion successful for provider: %s", provider)
            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump() if response.usage else None,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }

        except HTTPException:
            raise
        except AuthenticationError as e:
            logger.error("Authentication error for %s: %s", provider, e)
            raise HTTPException(status_code=401, detail=f"Invalid API key for {provider}") from e
        except RateLimitError as e:
            logger.error("Rate limit exceeded for %s: %s", provider, e)
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded for {provider}") from e
        except APIError as e:
            logger.error("API error for %s: %s", provider, e)
            raise HTTPException(status_code=502, detail=f"API error from {provider}") from e
        except Exception as e:
            logger.error("Unexpected error in LLM completion for %s: %s", provider, e)
            raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

    def get_available_models(self) -> dict[str, list[str]]:
        """Get available models for each configured provider.

        Returns
        -------
            Dictionary with provider names as keys and lists of available models as values

        """
        models = {}

        if self.config.openrouter_api_key:
            models["openrouter"] = [
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "anthropic/claude-3-haiku",
                "openai/gpt-4o",
                "openai/gpt-4o-mini",
                "meta-llama/llama-3.1-405b-instruct",
                "meta-llama/llama-3.1-70b-instruct",
                "meta-llama/llama-3.1-8b-instruct",
                "xiaomi/mimo-v2-flash:free",
            ]

        if self.config.groq_api_key:
            models["groq"] = [
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "llama3-8b-8192",
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma-7b-it",
            ]

        return models

    def get_providers_status(self) -> dict[str, dict[str, Any]]:
        """Get status of configured providers.

        Returns
        -------
            Dictionary with provider configuration status

        """
        return {
            "openrouter": {
                "configured": bool(self.config.openrouter_api_key),
                "default_model": self.config.openrouter_model,
            },
            "groq": {
                "configured": bool(self.config.groq_api_key),
                "default_model": self.config.groq_model,
            },
        }
