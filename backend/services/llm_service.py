"""
LLM Service - Unified interface for LLM providers through LiteLLM
"""
import os
import logging
from typing import Dict, Any, Optional, List
from litellm import completion, acompletion
from litellm.exceptions import APIError, RateLimitError, AuthenticationError
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Environment configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "")

# Explicitly set the keys for LiteLLM
os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

class LLMService:
    """Service for interacting with LLMs through LiteLLM"""

    @staticmethod
    def _get_completion_params(
        provider: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get provider-specific completion parameters

        Args:
            provider: The LLM provider ('openrouter' or 'groq')
            model: Optional specific model name, otherwise uses default

        Returns:
            Dict of parameters for litellm completion call

        Raises:
            HTTPException: If provider is not supported or API key missing
        """
        if provider == "openrouter":
            if not OPENROUTER_API_KEY:
                raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

            model_name = model or OPENROUTER_MODEL

            return {
                "model": f"{model_name}"
            }

        elif provider == "groq":
            if not GROQ_API_KEY:
                raise HTTPException(status_code=500, detail="Groq API key not configured")

            model_name = model or GROQ_MODEL

            return {
                "model": f"{model_name}"
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    @staticmethod
    async def generate_completion(
        provider: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion using the specified provider through LiteLLM

        Args:
            provider: LLM provider ('openrouter' or 'groq')
            messages: List of message dictionaries with 'role' and 'content'
            model: Optional model name, uses default if not provided
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the model

        Returns:
            Completion response dict with 'content', 'usage', 'model', 'finish_reason'

        Raises:
            HTTPException: For configuration errors, API errors, rate limits, etc.
        """
        try:
            params = LLMService._get_completion_params(provider, model)

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

            response = await acompletion(**completion_params)

            logger.info(f"LLM completion successful for provider: {provider}")

            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump() if response.usage else None,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }

        except HTTPException:
            raise
        except AuthenticationError as e:
            logger.error(f"Authentication error for {provider}: {e}")
            raise HTTPException(status_code=401, detail=f"Invalid API key for {provider}")
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded for {provider}: {e}")
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded for {provider}")
        except APIError as e:
            logger.error(f"API error for {provider}: {e}")
            raise HTTPException(status_code=502, detail=f"API error from {provider}")
        except Exception as e:
            logger.error(f"Unexpected error in LLM completion for {provider}: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

    @staticmethod
    def generate_completion_sync(
        provider: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Synchronous version of generate_completion

        Args:
            provider: LLM provider ('openrouter' or 'groq')
            messages: List of message dictionaries with 'role' and 'content'
            model: Optional model name, uses default if not provided
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the model

        Returns:
            Completion response dict with 'content', 'usage', 'model', 'finish_reason'

        Raises:
            HTTPException: For configuration errors, API errors, rate limits, etc.
        """
        try:
            params = LLMService._get_completion_params(provider, model)

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

            response = completion(**completion_params)

            logger.info(f"LLM completion successful for provider: {provider}")
            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump() if response.usage else None,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }

        except HTTPException:
            raise
        except AuthenticationError as e:
            logger.error(f"Authentication error for {provider}: {e}")
            raise HTTPException(status_code=401, detail=f"Invalid API key for {provider}")
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded for {provider}: {e}")
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded for {provider}")
        except APIError as e:
            logger.error(f"API error for {provider}: {e}")
            raise HTTPException(status_code=502, detail=f"API error from {provider}")
        except Exception as e:
            logger.error(f"Unexpected error in LLM completion for {provider}: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

    @staticmethod
    def get_available_models() -> Dict[str, List[str]]:
        """
        Get available models for each configured provider

        Returns:
            Dictionary with provider names as keys and lists of available models as values
        """
        models = {}

        if OPENROUTER_API_KEY:
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

        if GROQ_API_KEY:
            models["groq"] = [
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "llama3-8b-8192",
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma-7b-it",
            ]

        return models

    @staticmethod
    def get_providers_status() -> Dict[str, Dict[str, Any]]:
        """
        Get status of configured providers

        Returns:
            Dictionary with provider configuration status
        """
        return {
            "openrouter": {
                "configured": bool(OPENROUTER_API_KEY),
                "default_model": OPENROUTER_MODEL,
            },
            "groq": {
                "configured": bool(GROQ_API_KEY),
                "default_model": GROQ_MODEL,
            },
        }
