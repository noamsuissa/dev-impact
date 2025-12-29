"""
Badges Router - Handle badge system endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks

from backend.schemas.badge import (
    BadgeDefinition,
    UserBadge,
    UserBadgeWithDetails,
    BadgeProgress,
    BadgeStatsResponse,
    ListBadgesResponse,
    UserBadgesResponse,
    BadgeProgressResponse,
    CalculateBadgesRequest,
)
from backend.services.badges.badge_service import BadgeService
from backend.utils import auth_utils
from backend.utils.dependencies import ServiceDBClient

router = APIRouter(
    prefix="/api/badges",
    tags=["badges"],
)


@router.get("", response_model=ListBadgesResponse)
def list_badges(
    client: ServiceDBClient,
):
    """
    List all active badge definitions.
    
    Returns a list of all badges available to be earned.
    """
    return BadgeService.get_badge_definitions(client)


@router.get("/user", response_model=UserBadgesResponse)
def get_user_badges(
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Get badges earned by the current user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    return BadgeService.get_user_badges(client, user_id)


@router.get("/user/stats", response_model=BadgeStatsResponse)
def get_user_badge_stats(
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Get badge statistics for the current user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    return BadgeService.get_user_badge_stats(client, user_id)


@router.get("/user/progress", response_model=BadgeProgressResponse)
def get_user_badge_progress(
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Get progress towards badges for the current user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    return BadgeService.get_user_badge_progress(client, user_id)


@router.post("/calculate", response_model=UserBadgesResponse)
def calculate_badges(
    request: CalculateBadgesRequest,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Trigger badge calculation for the current user.
    
    This evaluates the user's projects and metrics against badge definitions
    and awards any satisfied badges.
    """
    
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    return BadgeService.calculate_badges(
        client, 
        user_id, 
        request.project_ids
    )


@router.get("/{badge_id}", response_model=BadgeDefinition)
def get_badge_definition(
    badge_id: str,
    client: ServiceDBClient,
):
    """
    Get details for a specific badge definition.
    """
    return BadgeService.get_badge_definition(client, badge_id)
