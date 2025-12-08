"""
Project Schemas - Pydantic models for project operations
"""
from pydantic import BaseModel, field_serializer
from typing import Optional, List, Union
from datetime import datetime


class ProjectMetric(BaseModel):
    """Project metric schema"""
    primary: str
    label: str
    detail: Optional[str] = None


class Project(BaseModel):
    """Project schema"""
    id: Optional[str] = None
    company: str
    projectName: str
    role: str
    teamSize: int
    problem: str
    contributions: List[str]
    techStack: List[str]
    metrics: List[ProjectMetric]
    profile_id: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project response with database fields"""
    id: str
    user_id: str
    company: str
    project_name: str
    role: str
    team_size: int
    problem: str
    contributions: List[str]
    tech_stack: List[str]
    display_order: int
    profile_id: Optional[str] = None
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]
    metrics: List[ProjectMetric]
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: Union[str, datetime]) -> str:
        """Convert datetime to ISO format string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class CreateProjectRequest(BaseModel):
    """Create project request"""
    company: str
    projectName: str
    role: str
    teamSize: int
    problem: str
    contributions: List[str]
    techStack: List[str]
    metrics: List[ProjectMetric]
    profile_id: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    """Update project request"""
    company: Optional[str] = None
    projectName: Optional[str] = None
    role: Optional[str] = None
    teamSize: Optional[int] = None
    problem: Optional[str] = None
    contributions: Optional[List[str]] = None
    techStack: Optional[List[str]] = None
    metrics: Optional[List[ProjectMetric]] = None
    profile_id: Optional[str] = None

