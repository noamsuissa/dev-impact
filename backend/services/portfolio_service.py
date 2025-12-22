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
from backend.utils.auth_utils import get_supabase_client
from backend.services.user_service import UserService
from backend.services.project_service import ProjectService
from backend.services.subscription_service import SubscriptionService
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
        user_id: str,
        name: str,
        description: Optional[str] = None,
        token: Optional[str] = None
    ) -> Portfolio:
        """
        Create a new portfolio
        
        Args:
            user_id: The authenticated user's ID
            name: Portfolio name
            description: Optional portfolio description
            token: Optional user token for auth
            
        Returns:
            Portfolio containing created portfolio data
        """
        try:
            if not name or not name.strip():
                raise HTTPException(status_code=400, detail="Portfolio name is required")
            
            supabase = get_supabase_client(access_token=token)
            
            # Generate slug from name
            base_slug = PortfolioService.generate_slug(name)
            slug = base_slug
            
            # Ensure slug is unique per user
            counter = 1
            while True:
                existing = supabase.table("portfolios")\
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
            
            # Check portfolio limit before creating
            subscription_info = await SubscriptionService.get_subscription_info(user_id, token)
            if not subscription_info.can_add_profile:
                raise HTTPException(
                    status_code=403,
                    detail=f"Portfolio limit reached. Free users are limited to {subscription_info.max_profiles} portfolios. Upgrade to Pro for unlimited portfolios."
                )
            
            # Get current portfolio count for display_order
            count_result = supabase.table("portfolios")\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .execute()
            
            display_order = len(count_result.data) if count_result.data else 0
            
            # Insert new portfolio
            result = supabase.table("portfolios").insert({
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
        user_id: str,
        token: Optional[str] = None
    ) -> List[Portfolio]:
        """
        List all portfolios for a user
        
        Args:
            user_id: The user's ID
            token: Optional user token for auth
            
        Returns:
            List of Portfolio objects
        """
        try:
            supabase = get_supabase_client(access_token=token)
            
            result = supabase.table("portfolios")\
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
        portfolio_id: str,
        user_id: str,
        token: Optional[str] = None
    ) -> Portfolio:
        """
        Get a single portfolio
        
        Args:
            portfolio_id: The portfolio ID
            user_id: The user's ID (for authorization)
            token: Optional user token for auth
            
        Returns:
            Portfolio object
        """
        try:
            supabase = get_supabase_client(access_token=token)
            
            result = supabase.table("portfolios")\
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
        portfolio_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        token: Optional[str] = None
    ) -> Portfolio:
        """
        Update a portfolio
        
        Args:
            portfolio_id: The portfolio ID
            user_id: The user's ID (for authorization)
            name: Optional new name
            description: Optional new description
            token: Optional user token for auth
            
        Returns:
            Updated Portfolio object
        """
        try:
            supabase = get_supabase_client(access_token=token)
            
            # Verify ownership
            existing = supabase.table("portfolios")\
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
                    check_result = supabase.table("portfolios")\
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
            result = supabase.table("portfolios")\
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
        portfolio_id: str,
        user_id: str,
        token: Optional[str] = None
    ) -> MessageResponse:
        """
        Delete a portfolio
        
        Args:
            portfolio_id: The portfolio ID
            user_id: The user's ID (for authorization)
            token: Optional user token for auth
            
        Returns:
            MessageResponse with success status
        """
        try:
            supabase = get_supabase_client(access_token=token)
            
            # Verify ownership
            existing = supabase.table("portfolios")\
                .select("user_id")\
                .eq("id", portfolio_id)\
                .execute()
            
            if not existing.data or len(existing.data) == 0:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            if existing.data[0]["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="You don't have permission to delete this portfolio")
            
            # Delete all projects assigned to this portfolio first
            supabase.table("impact_projects")\
                .delete()\
                .eq("profile_id", portfolio_id)\
                .eq("user_id", user_id)\
                .execute()
            
            # Delete portfolio
            result = supabase.table("portfolios")\
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
    async def publish_portfolio(username: str, portfolio_id: str, user_id: str, token: str) -> PublishPortfolioResponse:
        """
        Publish a portfolio with a username
        
        Args:
            username: The user's username for publishing
            portfolio_id: The portfolio ID to publish
            user_id: The authenticated user's ID
            token: The user's auth token
            
        Returns:
            PublishPortfolioResponse with success status, username, slug, and URL
        """
        try:
            if not PortfolioService.validate_username(username):
                raise HTTPException(status_code=400, detail="Username must be 3-50 characters, lowercase letters, numbers, and hyphens only")
            
            # Ensure username consistency (lowercase)
            username = username.lower()
            
            supabase = get_supabase_client(access_token=token)
            
            # Verify portfolio exists and belongs to user
            portfolio_result = supabase.table("portfolios")\
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
            existing = supabase.table("published_profiles")\
                .select("user_id, profile_id")\
                .eq("username", username)\
                .eq("profile_slug", portfolio_slug)\
                .execute()
            
            if existing.data and len(existing.data) > 0:
                existing_profile = existing.data[0]
                if existing_profile.get("user_id") and existing_profile["user_id"] != user_id:
                    raise HTTPException(status_code=409, detail="This portfolio slug is already taken for this username")
            
            # Fetch latest user profile from database
            try:
                user_profile = await UserService.get_profile(user_id)
                user_profile_data = user_profile.model_dump()
            except Exception as e:
                print(f"Error fetching user profile: {e}")
                raise HTTPException(status_code=500, detail="Failed to fetch user profile")
            
            # Fetch latest projects from database for this portfolio
            try:
                projects = await ProjectService.list_projects(user_id, profile_id=portfolio_id, include_evidence=True)
                projects_data = [project.model_dump() for project in projects]
            except Exception as e:
                print(f"Error fetching projects: {e}")
                raise HTTPException(status_code=500, detail="Failed to fetch projects")
            
            # Build portfolio_data from fresh database data
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
            existing = supabase.table("published_profiles")\
                .select("id")\
                .eq("username", username)\
                .eq("profile_slug", portfolio_slug)\
                .execute()
            
            # Insert or update published portfolio with fresh data
            if existing.data and len(existing.data) > 0:
                # Update existing
                result = supabase.table("published_profiles")\
                    .update({
                        "profile_id": portfolio_id,
                        "profile_data": fresh_portfolio_data,
                        "is_published": True,
                        "updated_at": datetime.utcnow().isoformat()
                    })\
                    .eq("username", username)\
                    .eq("profile_slug", portfolio_slug)\
                    .execute()
            else:
                # Insert new
                result = supabase.table("published_profiles")\
                    .insert({
                        "user_id": user_id,
                        "username": username,
                        "profile_id": portfolio_id,
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
    async def unpublish_portfolio(username: str, portfolio_slug: str, user_id: str) -> MessageResponse:
        """
        Unpublish a portfolio
        
        Args:
            username: The profile username
            portfolio_slug: The portfolio slug to unpublish
            user_id: The authenticated user's ID
            
        Returns:
            MessageResponse with success status and message
        """
        try:
            supabase = get_supabase_client()
            
            # Verify ownership via profile_id
            result = supabase.table("published_profiles")\
                .select("profile_id, portfolios!inner(user_id)")\
                .eq("username", username)\
                .eq("profile_slug", portfolio_slug)\
                .execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            # Check ownership via profile_id relationship
            profile_id = result.data[0].get("profile_id")
            if profile_id:
                portfolio_check = supabase.table("portfolios")\
                    .select("user_id")\
                    .eq("id", profile_id)\
                    .single()\
                    .execute()
                
                if portfolio_check.data and portfolio_check.data["user_id"] != user_id:
                    raise HTTPException(status_code=403, detail="You don't have permission to unpublish this portfolio")
            
            # Unpublish (set is_published to false)
            supabase.table("published_profiles")\
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
    async def get_published_portfolio(username: str, portfolio_slug: Optional[str] = None) -> PortfolioResponse:
        """
        Get a published portfolio by username and optional portfolio slug (PUBLIC)
        
        Args:
            username: The profile username to fetch
            portfolio_slug: Optional portfolio slug (for multi-portfolio support)
            
        Returns:
            PortfolioResponse containing portfolio data
        """
        try:
            if not PortfolioService.validate_username(username):
                raise HTTPException(status_code=400, detail="Invalid username format")
            
            supabase = get_supabase_client()
            
            # Build query
            query = supabase.table("published_profiles")\
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
                update_query = supabase.table("published_profiles")\
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
    async def list_published_portfolios(limit: int = 50, offset: int = 0) -> ListPortfoliosResponse:
        """
        List all published portfolios (PUBLIC)
        
        Args:
            limit: Maximum number of portfolios to return
            offset: Number of portfolios to skip
            
        Returns:
            ListPortfoliosResponse containing portfolios list and pagination info
        """
        try:
            supabase = get_supabase_client()
            
            result = supabase.table("published_profiles")\
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

