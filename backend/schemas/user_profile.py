"""
User Profile Schemas - For managing user profiles (project organization profiles)
"""
from pydantic import BaseModel
from typing import Optional


class UserProfile(BaseModel):
    """User profile schema - represents a profile for organizing projects"""
    id: str
    name: str
    description: Optional[str] = None
    slug: str
    display_order: int
    created_at: str
    updated_at: str


class CreateUserProfileRequest(BaseModel):
    """Create user profile request"""
    name: str
    description: Optional[str] = None


class UpdateUserProfileRequest(BaseModel):
    """Update user profile request"""
    name: Optional[str] = None
    description: Optional[str] = None

