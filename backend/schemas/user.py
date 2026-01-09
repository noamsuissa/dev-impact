"""User Schemas - Pydantic models for user profile operations"""

from datetime import datetime

from pydantic import BaseModel, field_serializer


class GitHubInfo(BaseModel):
    """GitHub information"""

    username: str | None = None
    avatar_url: str | None = None


class UserProfile(BaseModel):
    """User profile schema"""

    id: str
    username: str | None = None
    full_name: str | None = None
    github_username: str | None = None
    github_avatar_url: str | None = None
    city: str | None = None
    country: str | None = None
    is_published: bool = False
    created_at: str | datetime
    updated_at: str | datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: str | datetime) -> str:
        """Convert datetime to ISO format string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class UpdateProfileRequest(BaseModel):
    """Update profile request"""

    full_name: str | None = None
    github_username: str | None = None
    github_avatar_url: str | None = None
    city: str | None = None
    country: str | None = None


class OnboardingRequest(BaseModel):
    """Onboarding request"""

    username: str
    name: str
    github: GitHubInfo | None = None
    city: str | None = None
    country: str | None = None


class CheckUsernameResponse(BaseModel):
    """Response for checking username availability"""

    available: bool
    valid: bool
    message: str | None = None
