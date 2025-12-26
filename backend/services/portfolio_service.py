"""
Portfolio Service - Unified service for portfolio CRUD and publishing operations
Merges functionality from user_profile_service.py and profile_service.py
"""
import os
import re
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
from fastapi import HTTPException
# Note: No cross-service imports - services are fully decoupled
# Router layer orchestrates multi-service workflows
from backend.schemas.portfolio import (
    Portfolio,
    PublishPortfolioResponse,
    PortfolioResponse,
    ListPortfoliosResponse,
    UserData,
    GitHubData,
    PortfolioData,
)
from backend.schemas.auth import MessageResponse
from backend.schemas.subscription import SubscriptionInfoResponse

# Load environment variables
load_dotenv()


class PortfolioService:
    """Unified service for handling portfolio operations (CRUD + Publishing)"""

    # ============================================
    # HELPER/VALIDATION METHODS
    # ============================================

    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        # Lowercase alphanumeric and hyphens only, 3-50 characters
        pattern = r'^[a-z0-9-]{3,50}$'
        return bool(re.match(pattern, username))

    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate URL-friendly slug from portfolio name"""
        if not name:
            return ""
        # Convert to lowercase, replace spaces and special chars with dashes
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower())
        # Remove leading/trailing dashes
        slug = slug.strip('-')
        # Ensure it's not empty
        if not slug:
            slug = "portfolio"
        return slug

    @staticmethod
    def validate_slug(slug: str) -> bool:
        """Validate slug format"""
        if not slug:
            return False
        # Lowercase alphanumeric and hyphens only, 1-100 characters
        pattern = r'^[a-z0-9-]{1,100}$'
        return bool(re.match(pattern, slug))

    # ============================================
    # PORTFOLIO CRUD OPERATIONS
    # ============================================

    @staticmethod
    async def create_portfolio(
        client,
        subscription_info: SubscriptionInfoResponse,
        user_id: str,
        name: str,
        description: Optional[str] = None
    ) -> Portfolio:
        """
        Create a new portfolio
        
        Args:
            client: Supabase client (injected from router)
            subscription_info: Subscription information
            user_id: The authenticated user's ID
            name: Portfolio name
            description: Optional portfolio description
            
        Returns:
            Portfolio containing created portfolio data
        """
        if not subscription_info.can_add_portfolio:
            raise HTTPException(
                status_code=403,
                detail=f"Portfolio limit reached. Free users are limited to {subscription_info.max_portfolios} portfolios. Upgrade to Pro for unlimited portfolios."
            )
        try:
            if not name or not name.strip():
                raise HTTPException(status_code=400, detail="Portfolio name is required")
            
            # Generate slug from name
            base_slug = PortfolioService.generate_slug(name)
            slug = base_slug
            
            # Ensure slug is unique per user
            counter = 1
            while True:
                existing = client.table("portfolios")\
                    .select("id")\
                    .eq("user_id", user_id)\
                    .eq("slug", slug)\
                    .execute()
                
                if not existing.data or len(existing.data) == 0:
                    break
                
                slug = f"{base_slug}-{counter}"
                counter += 1
                
                # Safety check to prevent infinite loop
                if counter > 1000:
                    raise HTTPException(status_code=500, detail="Failed to generate unique slug")
            
            # Get current portfolio count for display_order
            count_result = client.table("portfolios")\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .execute()
            
            display_order = len(count_result.data) if count_result.data else 0
            
            # Insert new portfolio
            result = client.table("portfolios").insert({
                "user_id": user_id,
                "name": name.strip(),
                "description": description.strip() if description else None,
                "slug": slug,
                "display_order": display_order
            }).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=500, detail="Failed to create portfolio")
            
            portfolio = result.data[0]
            return Portfolio(
                id=portfolio["id"],
                name=portfolio["name"],
                description=portfolio.get("description"),
                slug=portfolio["slug"],
                display_order=portfolio["display_order"],
                created_at=portfolio["created_at"],
                updated_at=portfolio["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Create portfolio error: {e}")
            raise HTTPException(status_code=500, detail="Failed to create portfolio")

    @staticmethod
    async def list_portfolios(
        client,
        user_id: str
    ) -> List[Portfolio]:
        """
        List all portfolios for a user
        
        Args:
            client: Supabase client (injected from router)
            user_id: The user's ID
            
        Returns:
            List of Portfolio objects
        """
        try:
            result = client.table("portfolios")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("display_order")\
                .order("created_at")\
                .execute()
            
            portfolios = []
            for portfolio in result.data:
                portfolios.append(Portfolio(
                    id=portfolio["id"],
                    name=portfolio["name"],
                    description=portfolio.get("description"),
                    slug=portfolio["slug"],
                    display_order=portfolio["display_order"],
                    created_at=portfolio["created_at"],
                    updated_at=portfolio["updated_at"]
                ))
            
            return portfolios
        except HTTPException:
            raise
        except Exception as e:
            print(f"List portfolios error: {e}")
            raise HTTPException(status_code=500, detail="Failed to list portfolios")

    @staticmethod
    async def get_portfolio(
        client,
        portfolio_id: str,
        user_id: str
    ) -> Portfolio:
        """
        Get a single portfolio
        
        Args:
            client: Supabase client (injected from router)
            portfolio_id: The portfolio ID
            user_id: The user's ID (for authorization)
            
        Returns:
            Portfolio object
        """
        try:
            result = client.table("portfolios")\
                .select("*")\
                .eq("id", portfolio_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            portfolio = result.data
            return Portfolio(
                id=portfolio["id"],
                name=portfolio["name"],
                description=portfolio.get("description"),
                slug=portfolio["slug"],
                display_order=portfolio["display_order"],
                created_at=portfolio["created_at"],
                updated_at=portfolio["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get portfolio error: {e}")
            raise HTTPException(status_code=500, detail="Failed to get portfolio")

    @staticmethod
    async def update_portfolio(
        client,
        portfolio_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Portfolio:
        """
        Update a portfolio
        
        Args:
            client: Supabase client (injected from router)
            portfolio_id: The portfolio ID
            user_id: The user's ID (for authorization)
            name: Optional new name
            description: Optional new description
            
        Returns:
            Updated Portfolio object
        """
        try:
            # Verify ownership
            existing = client.table("portfolios")\
                .select("user_id, slug")\
                .eq("id", portfolio_id)\
                .execute()
            
            if not existing.data or len(existing.data) == 0:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            if existing.data[0]["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="You don't have permission to update this portfolio")
            
            # Prepare update data
            update_data = {}
            if name is not None:
                if not name.strip():
                    raise HTTPException(status_code=400, detail="Portfolio name cannot be empty")
                update_data["name"] = name.strip()
                # Regenerate slug if name changed
                new_slug = PortfolioService.generate_slug(name.strip())
                # Ensure uniqueness
                base_slug = new_slug
                counter = 1
                while True:
                    check_result = client.table("portfolios")\
                        .select("id")\
                        .eq("user_id", user_id)\
                        .eq("slug", new_slug)\
                        .neq("id", portfolio_id)\
                        .execute()
                    
                    if not check_result.data or len(check_result.data) == 0:
                        break
                    
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
                    
                    if counter > 1000:
                        raise HTTPException(status_code=500, detail="Failed to generate unique slug")
                update_data["slug"] = new_slug
            
            if description is not None:
                update_data["description"] = description.strip() if description else None
            
            if not update_data:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            # Update portfolio
            result = client.table("portfolios")\
                .update(update_data)\
                .eq("id", portfolio_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=500, detail="Failed to update portfolio")
            
            portfolio = result.data[0]
            return Portfolio(
                id=portfolio["id"],
                name=portfolio["name"],
                description=portfolio.get("description"),
                slug=portfolio["slug"],
                display_order=portfolio["display_order"],
                created_at=portfolio["created_at"],
                updated_at=portfolio["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Update portfolio error: {e}")
            raise HTTPException(status_code=500, detail="Failed to update portfolio")

    @staticmethod
    async def delete_portfolio(
        client,
        portfolio_id: str,
        user_id: str
    ) -> MessageResponse:
        """
        Delete a portfolio
        
        Args:
            client: Supabase client (injected from router)
            portfolio_id: The portfolio ID
            user_id: The user's ID (for authorization)
            
        Returns:
            MessageResponse with success status
        """
        try:
            # Verify ownership
            existing = client.table("portfolios")\
                .select("user_id")\
                .eq("id", portfolio_id)\
                .execute()
            
            if not existing.data or len(existing.data) == 0:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            if existing.data[0]["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="You don't have permission to delete this portfolio")
            
            # Delete all projects assigned to this portfolio first
            client.table("impact_projects")\
                .delete()\
                .eq("portfolio_id", portfolio_id)\
                .eq("user_id", user_id)\
                .execute()
            
            # Delete portfolio
            result = client.table("portfolios")\
                .delete()\
                .eq("id", portfolio_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return MessageResponse(
                success=True,
                message="Portfolio and all assigned projects deleted successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Delete portfolio error: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete portfolio")

    # ============================================
    # PUBLISHING OPERATIONS
    # ============================================

    @staticmethod
    async def publish_portfolio(client, username: str, portfolio_id: str, user_profile, projects: List, user_id: str | None = None) -> PublishPortfolioResponse:
        """
        Publish a portfolio with a username
        
        Args:
            client: Supabase client (injected from router)
            username: The user's username for publishing
            portfolio_id: The portfolio ID to publish
            user_id: The authenticated user's ID
            user_profile: Pre-fetched user profile (UserProfile model)
            projects: Pre-fetched list of projects (List[Project])
            
        Returns:
            PublishPortfolioResponse with success status, username, slug, and URL
        """
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        try:
            if not PortfolioService.validate_username(username):
                raise HTTPException(status_code=400, detail="Username must be 3-50 characters, lowercase letters, numbers, and hyphens only")
            
            # Ensure username consistency (lowercase)
            username = username.lower()
            
            # Verify portfolio exists and belongs to user
            portfolio_result = client.table("portfolios")\
                .select("id, slug, name, description")\
                .eq("id", portfolio_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not portfolio_result.data:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            portfolio = portfolio_result.data
            portfolio_slug = portfolio["slug"]
            
            # Check if this portfolio is already published by another user
            existing = client.table("published_profiles")\
                .select("user_id, portfolio_id")\
                .eq("username", username)\
                .eq("profile_slug", portfolio_slug)\
                .execute()
            
            if existing.data and len(existing.data) > 0:
                existing_profile = existing.data[0]
                if existing_profile.get("user_id") and existing_profile["user_id"] != user_id:
                    raise HTTPException(status_code=409, detail="This portfolio slug is already taken for this username")
            
            # Use pre-fetched data (orchestrated by router)
            user_profile_data = user_profile.model_dump()
            projects_data = [project.model_dump() for project in projects]
            
            # Build portfolio_data from pre-fetched data
            fresh_portfolio_data = {
                "user": {
                    "name": user_profile_data.get("full_name", ""),
                    "github": {
                        "username": user_profile_data.get("github_username"),
                        "avatar_url": user_profile_data.get("github_avatar_url")
                    } if user_profile_data.get("github_username") else None
                },
                "profile": {
                    "name": portfolio["name"],
                    "description": portfolio.get("description")
                },
                "projects": projects_data
            }
            
            # Check if portfolio is already published
            existing = client.table("published_profiles")\
                .select("id")\
                .eq("username", username)\
                .eq("profile_slug", portfolio_slug)\
                .execute()
            
            # Insert or update published portfolio with fresh data
            if existing.data and len(existing.data) > 0:
                # Update existing
                result = client.table("published_profiles")\
                    .update({
                        "portfolio_id": portfolio_id,
                        "profile_data": fresh_portfolio_data,
                        "is_published": True,
                        "updated_at": datetime.utcnow().isoformat()
                    })\
                    .eq("username", username)\
                    .eq("profile_slug", portfolio_slug)\
                    .execute()
            else:
                # Insert new
                result = client.table("published_profiles")\
                    .insert({
                        "user_id": user_id,
                        "username": username,
                        "portfolio_id": portfolio_id,
                        "profile_slug": portfolio_slug,
                        "profile_data": fresh_portfolio_data,
                        "is_published": True,
                        "updated_at": datetime.utcnow().isoformat()
                    })\
                    .execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to publish portfolio")
            
            # Get base domain from environment
            base_domain = os.getenv("BASE_DOMAIN", "dev-impact.io")
            
            # Generate URL: username.dev-impact.io/portfolio-slug
            url = f"https://{username}.{base_domain}/{portfolio_slug}"
            
            return PublishPortfolioResponse(
                success=True,
                username=username,
                portfolio_slug=portfolio_slug,
                url=url,
                message="Portfolio published successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in publish_portfolio: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while publishing the portfolio")

    @staticmethod
    async def unpublish_portfolio(client, username: str, portfolio_slug: str, user_id: str) -> MessageResponse:
        """
        Unpublish a portfolio
        
        Args:
            client: Supabase client (injected from router)
            username: The profile username
            portfolio_slug: The portfolio slug to unpublish
            user_id: The authenticated user's ID
            
        Returns:
            MessageResponse with success status and message
        """
        try:
            # Verify ownership via portfolio_id
            result = client.table("published_profiles")\
                .select("portfolio_id, portfolios!inner(user_id)")\
                .eq("username", username)\
                .eq("profile_slug", portfolio_slug)\
                .execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            # Check ownership via portfolio_id relationship
            portfolio_id = result.data[0].get("portfolio_id")
            if portfolio_id:
                portfolio_check = client.table("portfolios")\
                    .select("user_id")\
                    .eq("id", portfolio_id)\
                    .single()\
                    .execute()
                
                if portfolio_check.data and portfolio_check.data["user_id"] != user_id:
                    raise HTTPException(status_code=403, detail="You don't have permission to unpublish this portfolio")
            
            # Unpublish (set is_published to false)
            client.table("published_profiles")\
                .update({"is_published": False})\
                .eq("username", username)\
                .eq("profile_slug", portfolio_slug)\
                .execute()
            
            return MessageResponse(
                success=True,
                message="Portfolio unpublished successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to unpublish portfolio: {e}")

    # ============================================
    # PUBLIC PORTFOLIO VIEWING
    # ============================================

    @staticmethod
    async def get_published_portfolio(client, username: str, portfolio_slug: Optional[str] = None) -> PortfolioResponse:
        """
        Get a published portfolio by username and optional portfolio slug (PUBLIC)
        
        Args:
            client: Supabase client (injected from router)
            username: The profile username to fetch
            portfolio_slug: Optional portfolio slug (for multi-portfolio support)
            
        Returns:
            PortfolioResponse containing portfolio data
        """
        try:
            if not PortfolioService.validate_username(username):
                raise HTTPException(status_code=400, detail="Invalid username format")
            
            # Build query
            query = client.table("published_profiles")\
                .select("*")\
                .eq("username", username)\
                .eq("is_published", True)
            
            # If portfolio_slug is provided, filter by it
            if portfolio_slug:
                if not PortfolioService.validate_slug(portfolio_slug):
                    raise HTTPException(status_code=400, detail="Invalid portfolio slug format")
                query = query.eq("profile_slug", portfolio_slug)
            
            result = query.execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            # Get the first one (or the specific one if slug provided)
            portfolio = result.data[0]
            
            # Increment view count
            try:
                update_query = client.table("published_profiles")\
                    .update({"view_count": portfolio["view_count"] + 1})\
                    .eq("username", username)
                
                if portfolio_slug:
                    update_query = update_query.eq("profile_slug", portfolio_slug)
                else:
                    update_query = update_query.eq("id", portfolio["id"])
                
                update_query.execute()
            except Exception as e:
                print(f"Failed to increment view count: {e}")
            
            # Return portfolio data
            portfolio_data = portfolio["profile_data"]
            return PortfolioResponse(
                username=portfolio["username"],
                portfolio_slug=portfolio.get("profile_slug"),
                user=portfolio_data["user"],
                portfolio=portfolio_data.get("profile"),
                projects=portfolio_data["projects"],
                view_count=portfolio["view_count"] + 1,
                published_at=portfolio["published_at"],
                updated_at=portfolio["updated_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in get_published_portfolio: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching the portfolio")

    @staticmethod
    async def list_published_portfolios(client, limit: int = 50, offset: int = 0) -> ListPortfoliosResponse:
        """
        List all published portfolios (PUBLIC)
        
        Args:
            client: Supabase client (injected from router)
            limit: Maximum number of portfolios to return
            offset: Number of portfolios to skip
            
        Returns:
            ListPortfoliosResponse containing portfolios list and pagination info
        """
        try:
            result = client.table("published_profiles")\
                .select("username, profile_slug, profile_data, view_count, published_at, updated_at")\
                .eq("is_published", True)\
                .order("published_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            portfolios = []
            for portfolio in result.data:
                portfolio_data = portfolio["profile_data"]
                portfolios.append(
                    PortfolioResponse(
                        username=portfolio["username"],
                        portfolio_slug=portfolio.get("profile_slug"),
                        user=UserData(
                            name=portfolio_data["user"]["name"],
                            github=GitHubData(
                                username=portfolio_data["user"]
                                .get("github")
                                .get("username")
                                if portfolio_data["user"].get("github")
                                else None,
                                avatar_url=portfolio_data["user"]
                                .get("github")
                                .get("avatar_url")
                                if portfolio_data["user"].get("github")
                                else None,
                            ),
                        ),
                        portfolio=PortfolioData(
                            name=portfolio_data["profile"]["name"],
                            description=portfolio_data["profile"].get("description"),
                        ),
                        projects=portfolio_data["projects"],
                        view_count=portfolio["view_count"],
                        published_at=portfolio["published_at"],
                        updated_at=portfolio["updated_at"],
                    )
                )
            
            return ListPortfoliosResponse(
                portfolios=portfolios,
                total=len(portfolios),
                limit=limit,
                offset=offset
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in list_published_portfolios: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while listing the portfolios")

