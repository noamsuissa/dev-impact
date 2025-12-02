from pydantic import BaseModel, Field
from typing import List, Optional

# Pydantic models for request/response
class MetricData(BaseModel):
    primary: str
    label: str
    detail: Optional[str] = None

class ProjectData(BaseModel):
    id: str
    company: str
    projectName: str = Field(..., alias="projectName")
    role: str
    teamSize: Optional[int] = Field(None, alias="teamSize")
    problem: str
    contributions: List[str]
    techStack: List[str] = Field(..., alias="techStack")
    metrics: List[MetricData] = []

    class Config:
        populate_by_name = True

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

class PublishProfileResponse(BaseModel):
    success: bool
    username: str
    url: str
    message: str

class ProfileResponse(BaseModel):
    username: str
    user: UserData
    projects: List[ProjectData]
    viewCount: int = Field(..., alias="view_count")
    publishedAt: str = Field(..., alias="published_at")
    updatedAt: str = Field(..., alias="updated_at")

    class Config:
        populate_by_name = True