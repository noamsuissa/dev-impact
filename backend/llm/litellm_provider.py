"""
LLM Provider - Wrapper around LiteLLM for LLM interactions
"""
import os
import logging
from typing import Dict, Any, Optional, List
from litellm import completion, acompletion
from litellm.exceptions import APIError, RateLimitError, AuthenticationError

logger = logging.getLogger(__name__)

class LiteLLMProvider:
    """Provider for interacting with LLMs through LiteLLM"""
    
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.groq_model = os.getenv("GROQ_MODEL", "")
        
        # Explicitly set the keys for LiteLLM if they exist
        if self.openrouter_api_key:
            os.environ["OPENROUTER_API_KEY"] = self.openrouter_api_key
        if self.groq_api_key:
            os.environ["GROQ_API_KEY"] = self.groq_api_key

    def _get_model_string(self, provider: str, model: Optional[str] = None) -> str:
        """
        Get the provider-specific model string for LiteLLM
        """
        if provider == "openrouter":
            if not self.openrouter_api_key:
                raise ValueError("OpenRouter API key not configured")
            model_name = model or self.openrouter_model
            return f"openrouter/{model_name}"
            
        elif provider == "groq":
            if not self.groq_api_key:
                raise ValueError("Groq API key not configured")
            model_name = model or self.groq_model
            return f"groq/{model_name}"
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def generate_completion(
        self,
        provider: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion asynchronously
        """
        try:
            model_string = self._get_model_string(provider, model)
            
            completion_params = {
                "model": model_string,
                "messages": messages,
                "temperature": temperature,
                "user": user_id,
            }

            if max_tokens:
                completion_params["max_tokens"] = max_tokens

            # Merge additional kwargs
            for key, value in kwargs.items():
                if key not in completion_params:
                    completion_params[key] = value

            response: Any = await acompletion(**completion_params)
            
            logger.info(f"LLM completion successful for provider: {provider}")
            
            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump() if response.usage else None,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }
            
        except (ValueError, AuthenticationError, RateLimitError, APIError) as e:
            # Re-raise known exceptions to be handled by the service/caller
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in LLM completion for {provider}: {e}")
            raise RuntimeError(f"Unexpected error in LLM provider: {e}")

    def generate_completion_sync(
        self,
        provider: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion synchronously
        """
        try:
            model_string = self._get_model_string(provider, model)
            
            completion_params = {
                "model": model_string,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens:
                completion_params["max_tokens"] = max_tokens

            for key, value in kwargs.items():
                if key not in completion_params:
                    completion_params[key] = value

            response: Any = completion(**completion_params)
            
            logger.info(f"LLM completion successful for provider: {provider}")
            
            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump() if response.usage else None,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }
            
        except (ValueError, AuthenticationError, RateLimitError, APIError) as e:
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in LLM completion for {provider}: {e}")
            raise RuntimeError(f"Unexpected error in LLM provider: {e}")

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models for each configured provider"""
        models = {}

        if self.openrouter_api_key:
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

        if self.groq_api_key:
            models["groq"] = [
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "llama3-8b-8192",
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma-7b-it",
            ]

        return models

    def get_providers_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of configured providers"""
        return {
            "openrouter": {
                "configured": bool(self.openrouter_api_key),
                "default_model": self.openrouter_model,
            },
            "groq": {
                "configured": bool(self.groq_api_key),
                "default_model": self.groq_model,
            },
        }
