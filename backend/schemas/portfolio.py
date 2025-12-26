"""
Portfolio Schemas - For managing portfolios (project organization tabs that can be published)
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from backend.schemas.project import Project


# ============================================
# PORTFOLIO CRUD SCHEMAS (from user_profile.py)
# ============================================

class Portfolio(BaseModel):
    """Portfolio schema - represents a portfolio for organizing projects"""
    id: str
    name: str
    description: Optional[str] = None
    slug: str
    display_order: int
    created_at: str
    updated_at: str


class CreatePortfolioRequest(BaseModel):
    """Create portfolio request"""
    name: str
    description: Optional[str] = None


class UpdatePortfolioRequest(BaseModel):
    """Update portfolio request"""
    name: Optional[str] = None
    description: Optional[str] = None


# ============================================
# PUBLISHING SCHEMAS (from profile.py)
# ============================================

class GitHubData(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = Field(None, alias="avatar_url")

    class Config:
        populate_by_name = True


class UserData(BaseModel):
    name: str
    github: Optional[GitHubData] = None


class PublishPortfolioRequest(BaseModel):
    """Request to publish a portfolio"""
    username: str
    portfolio_id: str


class PublishPortfolioResponse(BaseModel):
    """Response after publishing a portfolio"""
    success: bool
    username: str
    portfolio_slug: str
    url: str
    message: str


class PortfolioData(BaseModel):
    """Published portfolio metadata"""
    name: str
    description: Optional[str] = None


class PortfolioResponse(BaseModel):
    """Public portfolio response (for viewing published portfolios)"""
    username: str
    portfolio_slug: Optional[str] = Field(None, alias="portfolio_slug")
    user: UserData
    portfolio: Optional[PortfolioData] = Field(None, alias="portfolio")
    projects: List[Project]
    view_count: int
    published_at: str
    updated_at: str

    class Config:
        populate_by_name = True


class ListPortfoliosResponse(BaseModel):
    """Response for listing published portfolios"""
    portfolios: Optional[List[PortfolioResponse]] = None
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

