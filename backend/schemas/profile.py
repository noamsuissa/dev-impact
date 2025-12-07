"""
Profile Schemas - For published profiles (user account profiles)
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from schemas.project import Project

class GitHubData(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = Field(None, alias="avatar_url")

    class Config:
        populate_by_name = True

class UserData(BaseModel):
    name: str
    github: Optional[GitHubData] = None

class PublishProfileRequest(BaseModel):
    username: str
    profile_id: str

class PublishProfileResponse(BaseModel):
    success: bool
    username: str
    profile_slug: str
    url: str
    message: str

class ProfileData(BaseModel):
    """Published profile metadata (user profile for projects)"""
    name: str
    description: Optional[str] = None


class ProfileResponse(BaseModel):
    username: str
    profile_slug: Optional[str] = None
    user: UserData
    profile: Optional[ProfileData] = None
    projects: List[Project]
    viewCount: int = Field(..., alias="view_count")
    publishedAt: str = Field(..., alias="published_at")
    updatedAt: str = Field(..., alias="updated_at")

    class Config:
        populate_by_name = True

class CheckUsernameResponse(BaseModel):
    available: bool
    valid: bool
    message: Optional[str] = None

class ListProfilesResponse(BaseModel):
    profiles: Optional[List[ProfileResponse]] = None
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None