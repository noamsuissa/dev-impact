"""
Projects Router - Handle project CRUD endpoints
"""
from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from schemas.project import Project, CreateProjectRequest, UpdateProjectRequest
from services.project_service import ProjectService
from utils import auth_utils
from schemas.auth import MessageResponse

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
)


@router.get("", response_model=List[Project])
async def list_projects(
    authorization: str = Depends(auth_utils.get_access_token),
    profile_id: Optional[str] = Query(None, description="Filter projects by profile ID")
):
    """
    List all projects for current user
    
    Returns all projects owned by the authenticated user, optionally filtered by profile.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    projects = await ProjectService.list_projects(user_id, profile_id=profile_id)
    return projects


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Get a single project by ID
    
    Returns project data if owned by the authenticated user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    project = await ProjectService.get_project(project_id, user_id)
    return project


@router.post("", response_model=Project)
async def create_project(
    request: CreateProjectRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Create a new project
    
    Creates a new project for the authenticated user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    project_data = request.model_dump()
    project = await ProjectService.create_project(user_id, project_data)
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Update a project
    
    Updates project data if owned by the authenticated user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    project_data = request.model_dump(exclude_none=True)
    project = await ProjectService.update_project(project_id, user_id, project_data)
    return project


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: str,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Delete a project
    
    Deletes project if owned by the authenticated user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    result = await ProjectService.delete_project(project_id, user_id)
    return result

