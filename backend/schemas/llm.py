"""LLM Schemas - Pydantic models for LLM operations"""

from typing import Any

from pydantic import BaseModel


class CompletionRequest(BaseModel):
    """Request model for LLM completion"""

    provider: str  # 'openrouter' or 'groq'
    messages: list[dict[str, str]]
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None


class CompletionResponse(BaseModel):
    """Response model for LLM completion"""

    content: str
    usage: dict[str, Any] | None = None
    model: str
    finish_reason: str | None = None
