"""
Portfolios Router - Unified router for portfolio CRUD and publishing operations
Merges endpoints from user_profile.py and profile.py
"""

from typing import List
from fastapi import APIRouter, Depends
from backend.schemas.portfolio import (
    Portfolio,
    CreatePortfolioRequest,
    UpdatePortfolioRequest,
    PublishPortfolioRequest,
    PublishPortfolioResponse,
    PortfolioResponse,
    ListPortfoliosResponse,
    PortfolioStatsResponse,
)
from backend.schemas.auth import MessageResponse
from backend.utils import auth_utils
from backend.core.container import (
    ServiceDBClient,
    PortfolioServiceDep,
    SubscriptionServiceDep,
    UserServiceDep,
    ProjectServiceDep,
)

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
    client: ServiceDBClient,
    portfolio_service: PortfolioServiceDep,
    subscription_service: SubscriptionServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Create a new portfolio

    Creates a portfolio that can group related projects.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)

    # Step 1: Check subscription limits (orchestration in router)
    subscription_info = await subscription_service.get_subscription_info(
        client, user_id
    )

    # Step 2: Create portfolio
    result = await portfolio_service.create_portfolio(
        client=client,
        subscription_info=subscription_info,
        user_id=user_id,
        name=portfolio.name,
        description=portfolio.description,
    )
    return result


@router.get("", response_model=List[Portfolio])
async def list_portfolios(
    client: ServiceDBClient,
    portfolio_service: PortfolioServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    List all portfolios for the authenticated user
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    portfolios = await portfolio_service.list_portfolios(client, user_id)
    return portfolios


@router.get("/published/stats", response_model=PortfolioStatsResponse)
async def get_published_portfolio_stats(
    client: ServiceDBClient,
    portfolio_service: PortfolioServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Get view count statistics for all of the authenticated user's portfolios

    This endpoint returns view counts for all portfolios (including unpublished ones).
    Only the portfolio owner can view their own statistics.

    NOTE: This must be defined BEFORE /published to avoid route conflicts.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await portfolio_service.get_published_portfolio_stats(client, user_id)
    return result


@router.get("/published", response_model=ListPortfoliosResponse)
async def list_published_portfolios(
    client: ServiceDBClient,
    portfolio_service: PortfolioServiceDep,
    limit: int = 50,
    offset: int = 0,
):
    """
    List all published portfolios (PUBLIC)

    This is a public endpoint that returns a list of all published portfolios.
    Useful for creating a directory or discovery feature.

    NOTE: This must be defined BEFORE /{portfolio_id} to avoid route conflicts.
    """
    result = await portfolio_service.list_published_portfolios(client, limit, offset)
    return result


@router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio(
    portfolio_id: str,
    client: ServiceDBClient,
    portfolio_service: PortfolioServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Get a single portfolio by ID
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    portfolio = await portfolio_service.get_portfolio(client, portfolio_id, user_id)
    return portfolio


@router.put("/{portfolio_id}", response_model=Portfolio)
async def update_portfolio(
    portfolio_id: str,
    portfolio: UpdatePortfolioRequest,
    client: ServiceDBClient,
    portfolio_service: PortfolioServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Update a portfolio
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await portfolio_service.update_portfolio(
        client,
        portfolio_id,
        user_id,
        name=portfolio.name,
        description=portfolio.description,
    )
    return result


@router.delete("/{portfolio_id}", response_model=MessageResponse)
async def delete_portfolio(
    portfolio_id: str,
    client: ServiceDBClient,
    portfolio_service: PortfolioServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Delete a portfolio
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await portfolio_service.delete_portfolio(client, portfolio_id, user_id)
    return result


# ============================================
# PUBLISHING ENDPOINTS (Authenticated)
# ============================================


@router.post("/{portfolio_id}/publish", response_model=PublishPortfolioResponse)
async def publish_portfolio(
    portfolio_id: str,
    publish_request: PublishPortfolioRequest,
    client: ServiceDBClient,
    portfolio_service: PortfolioServiceDep,
    user_service: UserServiceDep,
    project_service: ProjectServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Publish a portfolio with a username

    This endpoint creates or updates a published portfolio with a unique username.
    The portfolio will be accessible at {username}.{BASE_DOMAIN}/{portfolio-slug}
    """
    user_id = auth_utils.get_user_id_from_token(authorization)

    # Step 1: Fetch user profile (orchestration in router)
    user_profile = await user_service.get_profile(client, user_id)

    # Step 2: Fetch projects for this portfolio
    projects = await project_service.list_projects(
        client, user_id, portfolio_id=portfolio_id, include_evidence=True
    )

    # Step 3: Publish portfolio with pre-fetched data
    result = await portfolio_service.publish_portfolio(
        client=client,
        username=publish_request.username,
        portfolio_id=portfolio_id,
        user_id=user_id,
        user_profile=user_profile,
        projects=projects,
    )
    return result


@router.delete("/{username}/{portfolio_slug}", response_model=MessageResponse)
async def unpublish_portfolio(
    username: str,
    portfolio_slug: str,
    client: ServiceDBClient,
    portfolio_service: PortfolioServiceDep,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Unpublish a portfolio

    This endpoint unpublishes the portfolio (sets is_published to false).
    Only the portfolio owner can unpublish their portfolio.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    result = await portfolio_service.unpublish_portfolio(
        client, username, portfolio_slug, user_id
    )
    return result


# ============================================
# PUBLIC ENDPOINTS (No Authentication Required)
# ============================================


@router.get("/{username}/{portfolio_slug}", response_model=PortfolioResponse)
async def get_published_portfolio_with_slug(
    username: str,
    portfolio_slug: str,
    client: ServiceDBClient,
    portfolio_service: PortfolioServiceDep,
    increment: bool = True,
):
    """
    Get a published portfolio by username and portfolio slug (PUBLIC)

    This endpoint is public and doesn't require authentication.
    By default, it increments the view count each time it's accessed.
    Set ?increment=false to prevent incrementing the view count.

    URL format: /api/portfolios/{username}/{portfolio-slug}?increment=false
    """
    portfolio = await portfolio_service.get_published_portfolio(
        client, username, portfolio_slug, increment_view_count=increment
    )
    return portfolio
