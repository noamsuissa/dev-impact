"""
User Schemas - Pydantic models for user profile operations
"""

from pydantic import BaseModel, field_serializer
from typing import Optional, Union
from datetime import datetime


class GitHubInfo(BaseModel):
    """GitHub information"""

    username: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfile(BaseModel):
    """User profile schema"""

    id: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    github_username: Optional[str] = None
    github_avatar_url: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_published: bool = False
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: Union[str, datetime]) -> str:
        """Convert datetime to ISO format string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class UpdateProfileRequest(BaseModel):
    """Update profile request"""

    full_name: Optional[str] = None
    github_username: Optional[str] = None
    github_avatar_url: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class OnboardingRequest(BaseModel):
    """Onboarding request"""

    username: str
    name: str
    github: Optional[GitHubInfo] = None
    city: Optional[str] = None
    country: Optional[str] = None


class CheckUsernameResponse(BaseModel):
    """Response for checking username availability"""

    available: bool
    valid: bool
    message: Optional[str] = None
