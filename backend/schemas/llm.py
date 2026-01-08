from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class CompletionRequest(BaseModel):
    """Request model for LLM completion"""

    provider: str  # 'openrouter' or 'groq'
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class CompletionResponse(BaseModel):
    """Response model for LLM completion"""

    content: str
    usage: Optional[Dict[str, Any]] = None
    model: str
    finish_reason: Optional[str] = None
