"""
Portfolios Router - Unified router for portfolio CRUD and publishing operations
Merges endpoints from user_profile.py and profile.py
"""
from fastapi import APIRouter, Header, Depends
from typing import List, Optional
from backend.schemas.portfolio import (
    Portfolio,
    CreatePortfolioRequest,
    UpdatePortfolioRequest,
    PublishPortfolioRequest,
    PublishPortfolioResponse,
    PortfolioResponse,
    ListPortfoliosResponse,
)
from backend.schemas.auth import MessageResponse
from backend.services.portfolio_service import PortfolioService
from backend.utils import auth_utils

router = APIRouter(
    prefix="/api/portfolios",
    tags=["portfolios"],
)


# ============================================
# PORTFOLIO CRUD ENDPOINTS (Authenticated)
# ============================================

@router.post("", response_model=Portfolio)
async def create_portfolio(
    portfolio: CreatePortfolioRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Create a new portfolio
    
    Creates a portfolio that can group related projects.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await PortfolioService.create_portfolio(
        user_id=user_id,
        name=portfolio.name,
        description=portfolio.description,
        token=authorization
    )
    return result


@router.get("", response_model=List[Portfolio])
async def list_portfolios(
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    List all portfolios for the authenticated user
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    portfolios = await PortfolioService.list_portfolios(user_id, token=authorization)
    return portfolios


@router.get("/published", response_model=ListPortfoliosResponse)
async def list_published_portfolios(limit: int = 50, offset: int = 0):
    """
    List all published portfolios (PUBLIC)
    
    This is a public endpoint that returns a list of all published portfolios.
    Useful for creating a directory or discovery feature.
    
    NOTE: This must be defined BEFORE /{portfolio_id} to avoid route conflicts.
    """
    result = await PortfolioService.list_published_portfolios(limit, offset)
    return result


@router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio(
    portfolio_id: str,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Get a single portfolio by ID
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    portfolio = await PortfolioService.get_portfolio(portfolio_id, user_id, token=authorization)
    return portfolio


@router.put("/{portfolio_id}", response_model=Portfolio)
async def update_portfolio(
    portfolio_id: str,
    portfolio: UpdatePortfolioRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Update a portfolio
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await PortfolioService.update_portfolio(
        portfolio_id, 
        user_id, 
        name=portfolio.name, 
        description=portfolio.description, 
        token=authorization
    )
    return result


@router.delete("/{portfolio_id}", response_model=MessageResponse)
async def delete_portfolio(
    portfolio_id: str,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Delete a portfolio
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await PortfolioService.delete_portfolio(portfolio_id, user_id, token=authorization)
    return result


# ============================================
# PUBLISHING ENDPOINTS (Authenticated)
# ============================================

@router.post("/{portfolio_id}/publish", response_model=PublishPortfolioResponse)
async def publish_portfolio(
    portfolio_id: str,
    publish_request: PublishPortfolioRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Publish a portfolio with a username
    
    This endpoint creates or updates a published portfolio with a unique username.
    The portfolio will be accessible at {username}.{BASE_DOMAIN}/{portfolio-slug}
    """
    user_id = auth_utils.get_user_id_from_token(authorization)
    # Use the portfolio_id from the path parameter
    result = await PortfolioService.publish_portfolio(
        username=publish_request.username, 
        portfolio_id=portfolio_id,
        user_id=user_id, 
        token=authorization
    )
    return result


@router.delete("/{username}/{portfolio_slug}", response_model=MessageResponse)
async def unpublish_portfolio(
    username: str,
    portfolio_slug: str,
    authorization: Optional[str] = Header(None)
):
    """
    Unpublish a portfolio
    
    This endpoint unpublishes the portfolio (sets is_published to false).
    Only the portfolio owner can unpublish their portfolio.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await PortfolioService.unpublish_portfolio(username, portfolio_slug, user_id)
    return result


# ============================================
# PUBLIC ENDPOINTS (No Authentication Required)
# ============================================

@router.get("/{username}/{portfolio_slug}", response_model=PortfolioResponse)
async def get_published_portfolio_with_slug(username: str, portfolio_slug: str):
    """
    Get a published portfolio by username and portfolio slug (PUBLIC)
    
    This endpoint is public and doesn't require authentication.
    It increments the view count each time it's accessed.
    
    URL format: /api/portfolios/{username}/{portfolio-slug}
    """
    portfolio = await PortfolioService.get_published_portfolio(username, portfolio_slug)
    return portfolio

