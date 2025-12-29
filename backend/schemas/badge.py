"""
Badge Schemas - Pydantic models for badge operations
"""
from pydantic import BaseModel, field_serializer, Field
from typing import Optional, List, Dict, Any, Literal, Union
from datetime import datetime


# ============================================
# BADGE CATEGORY SCHEMAS
# ============================================

class BadgeCategory(BaseModel):
    """Badge category schema"""
    id: str
    name: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    display_order: int = 0
    total_badges: int = 0
    created_at: Union[str, datetime]
    
    @field_serializer('created_at')
    def serialize_datetime(self, value: Union[str, datetime]) -> str:
        """Convert datetime to ISO format string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value


# ============================================
# BADGE DEFINITION SCHEMAS
# ============================================

class BadgeDefinition(BaseModel):
    """Badge definition schema"""
    id: str
    badge_key: str
    name: str
    description: str
    category: str
    has_tiers: bool = True
    bronze_threshold: Optional[Dict[str, Any]] = None
    silver_threshold: Optional[Dict[str, Any]] = None
    gold_threshold: Optional[Dict[str, Any]] = None
    metric_type: Optional[str] = None
    calculation_type: Literal["aggregate", "single_project", "github_sync", "manual", "time_based"]
    calculation_logic: Optional[Dict[str, Any]] = None
    data_source: str = "project_metrics"
    requires_github: bool = False
    icon_name: Optional[str] = None
    color_scheme: Optional[Dict[str, str]] = None
    display_order: int = 0
    is_active: bool = True
    is_hidden: bool = False
    is_beta: bool = False
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]
    version: int = 1
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: Union[str, datetime]) -> str:
        """Convert datetime to ISO format string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value


# ============================================
# USER BADGE SCHEMAS
# ============================================

class UserBadge(BaseModel):
    """User badge schema - represents an earned badge"""
    id: str
    user_id: str
    badge_id: str
    portfolio_id: Optional[str] = None
    tier: Literal["bronze", "silver", "gold"]
    earned_at: Union[str, datetime]
    achievement_value: Optional[float] = None
    achievement_data: Optional[Dict[str, Any]] = None
    source_project_ids: Optional[List[str]] = None
    source_metric_ids: Optional[List[str]] = None
    github_data: Optional[Dict[str, Any]] = None
    is_featured: bool = False
    is_public: bool = True
    display_order: Optional[int] = None
    progress_to_next_tier: Optional[float] = None
    previous_tier: Optional[str] = None
    upgraded_at: Optional[Union[str, datetime]] = None
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]
    
    @field_serializer('earned_at', 'upgraded_at', 'created_at', 'updated_at')
    def serialize_datetime(self, value: Union[str, datetime, None]) -> Optional[str]:
        """Convert datetime to ISO format string"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class UserBadgeWithDetails(UserBadge):
    """User badge with badge definition details (from view)"""
    badge_key: str
    name: str  # Badge name from badge_definitions
    description: str  # Badge description from badge_definitions
    category: str  # Badge category from badge_definitions
    icon_name: Optional[str] = None  # From badge_definitions
    color_scheme: Optional[Dict[str, str]] = None  # From badge_definitions


# ============================================
# BADGE PROGRESS SCHEMAS
# ============================================

class BadgeProgress(BaseModel):
    """Badge progress schema - tracks progress toward earning a badge"""
    id: str
    user_id: str
    badge_id: str
    current_value: float
    target_value: float
    target_tier: Literal["bronze", "silver", "gold"]
    progress_percentage: float
    contributing_projects: Optional[List[str]] = None
    last_contribution_at: Optional[Union[str, datetime]] = None
    progress_data: Optional[Dict[str, Any]] = None
    first_tracked_at: Union[str, datetime]
    last_updated_at: Union[str, datetime]
    
    @field_serializer('last_contribution_at', 'first_tracked_at', 'last_updated_at')
    def serialize_datetime(self, value: Union[str, datetime, None]) -> Optional[str]:
        """Convert datetime to ISO format string"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return value


# ============================================
# BADGE AUDIT LOG SCHEMAS
# ============================================

class BadgeAuditLog(BaseModel):
    """Badge audit log schema - tracks badge-related events"""
    id: str
    user_id: str
    badge_id: str
    event_type: Literal["earned", "upgraded", "revoked", "progress_updated"]
    tier: Optional[str] = None
    old_value: Optional[float] = None
    new_value: Optional[float] = None
    event_data: Optional[Dict[str, Any]] = None
    triggered_by: Optional[str] = None
    created_at: Union[str, datetime]
    
    @field_serializer('created_at')
    def serialize_datetime(self, value: Union[str, datetime]) -> str:
        """Convert datetime to ISO format string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value


# ============================================
# REQUEST/RESPONSE SCHEMAS
# ============================================

class ListBadgesResponse(BaseModel):
    """Response for listing badge definitions"""
    badges: List[BadgeDefinition]
    total: int


class ListBadgeCategoriesResponse(BaseModel):
    """Response for listing badge categories"""
    categories: List[BadgeCategory]


class UserBadgesResponse(BaseModel):
    """Response for user's earned badges"""
    badges: List[UserBadgeWithDetails]
    total: int


class BadgeProgressResponse(BaseModel):
    """Response for user's badge progress"""
    progress: List[BadgeProgress]
    total: int


class BadgeStatsResponse(BaseModel):
    """Response for user badge statistics (from view)"""
    user_id: str
    total_badges: int
    bronze_count: int
    silver_count: int
    gold_count: int
    unique_badges: int
    most_recent_badge: Optional[Union[str, datetime]] = None
    badges_by_category: Optional[Dict[str, int]] = None
    
    @field_serializer('most_recent_badge')
    def serialize_datetime(self, value: Union[str, datetime, None]) -> Optional[str]:
        """Convert datetime to ISO format string"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class CalculateBadgesRequest(BaseModel):
    """Request to trigger badge calculation"""
    project_ids: Optional[List[str]] = None  # If None, calculates for all projects
    force_recalculate: bool = False  # Recalculate even if already earned


class AwardBadgeRequest(BaseModel):
    """Request to manually award a badge"""
    badge_id: str
    tier: Literal["bronze", "silver", "gold"]
    achievement_value: Optional[float] = None
    achievement_data: Optional[Dict[str, Any]] = None
    source_project_ids: Optional[List[str]] = None
    source_metric_ids: Optional[List[str]] = None
    portfolio_id: Optional[str] = None


class UpdateBadgeProgressRequest(BaseModel):
    """Request to update badge progress"""
    badge_id: str
    current_value: float
    target_tier: Literal["bronze", "silver", "gold"]
    contributing_projects: Optional[List[str]] = None
    progress_data: Optional[Dict[str, Any]] = None

