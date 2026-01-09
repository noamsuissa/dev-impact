"""LLM Router - API endpoints for LLM operations"""

from fastapi import APIRouter, Depends, HTTPException

from backend.core.container import LLMClientDep
from backend.schemas.llm import CompletionRequest, CompletionResponse
from backend.utils import auth_utils

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/completion", response_model=CompletionResponse)
async def generate_completion(
    request: CompletionRequest,
    llm_client: LLMClientDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """Generate a completion using the specified LLM provider

    This endpoint uses LiteLLM with Helicone observability to generate
    completions from OpenRouter or Groq providers.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)

    if request.provider not in ["openrouter", "groq"]:
        raise HTTPException(status_code=400, detail="Provider must be 'openrouter' or 'groq'")

    response = await llm_client.generate_completion(
        provider=request.provider,
        messages=request.messages,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        user_id=user_id,
    )

    return CompletionResponse(**response)


@router.get("/models")
async def get_available_models(llm_client: LLMClientDep):
    """Get available models for each configured provider

    Returns a dictionary with provider names as keys and lists of
    available models as values.
    """
    return llm_client.get_available_models()


@router.get("/providers")
async def get_providers_status(llm_client: LLMClientDep):
    """Get status of configured providers

    Returns information about which providers are configured and available.
    """
    return llm_client.get_providers_status()
