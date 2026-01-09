"""
Portfolio Schemas - For managing portfolios (project organization tabs that can be published)
"""

from pydantic import BaseModel, Field

from backend.schemas.project import Project

# ============================================
# PORTFOLIO CRUD SCHEMAS (from user_profile.py)
# ============================================


class Portfolio(BaseModel):
    """Portfolio schema - represents a portfolio for organizing projects"""

    id: str
    name: str
    description: str | None = None
    slug: str
    display_order: int
    created_at: str
    updated_at: str


class CreatePortfolioRequest(BaseModel):
    """Create portfolio request"""

    name: str
    description: str | None = None


class UpdatePortfolioRequest(BaseModel):
    """Update portfolio request"""

    name: str | None = None
    description: str | None = None


# ============================================
# PUBLISHING SCHEMAS (from profile.py)
# ============================================


class GitHubData(BaseModel):
    """GitHub data schema"""

    username: str | None = None
    avatar_url: str | None = Field(None, alias="avatar_url")

    class Config:
        """Config for GitHub data schema"""

        populate_by_name: bool = True


class UserData(BaseModel):
    """User data schema"""

    name: str
    github: GitHubData | None = None


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
    description: str | None = None


class PortfolioResponse(BaseModel):
    """Public portfolio response (for viewing published portfolios)"""

    username: str
    portfolio_slug: str | None = Field(None, alias="portfolio_slug")
    user: UserData
    portfolio: PortfolioData | None = Field(None, alias="portfolio")
    projects: list[Project]
    view_count: int
    published_at: str
    updated_at: str

    class Config:
        """Config for public portfolio response"""

        populate_by_name: bool = True


class ListPortfoliosResponse(BaseModel):
    """Response for listing published portfolios"""

    portfolios: list[PortfolioResponse] | None = None
    total: int | None = None
    limit: int | None = None
    offset: int | None = None


class PortfolioViewStats(BaseModel):
    """View count statistics for a portfolio"""

    portfolio_slug: str
    view_count: int
    is_published: bool


class PortfolioStatsResponse(BaseModel):
    """Response containing portfolio view statistics"""

    stats: list[PortfolioViewStats]
