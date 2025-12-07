"""
Projects Router - Handle project CRUD endpoints
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from schemas.project import Project, CreateProjectRequest, UpdateProjectRequest
from services.project_service import ProjectService
from services.auth.auth_service import AuthService
from utils import auth_utils

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
)


async def get_user_id_from_header(authorization: Optional[str]) -> str:
    """Extract and validate user ID from authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    access_token = authorization.replace("Bearer ", "")
    user_id = await auth_utils.verify_token(access_token)
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return user_id


@router.get("", response_model=List[Project])
async def list_projects(
    authorization: Optional[str] = Header(None),
    profile_id: Optional[str] = Query(None, description="Filter projects by profile ID")
):
    """
    List all projects for current user
    
    Returns all projects owned by the authenticated user, optionally filtered by profile.
    """
    user_id = await get_user_id_from_header(authorization)
    
    try:
        projects = await ProjectService.list_projects(user_id, profile_id=profile_id)
        return projects
    except HTTPException:
        raise
    except Exception as e:
        print(f"List projects error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch projects"
        )


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get a single project by ID
    
    Returns project data if owned by the authenticated user.
    """
    user_id = await get_user_id_from_header(authorization)
    
    try:
        project = await ProjectService.get_project(project_id, user_id)
        return project
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get project error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch project"
        )


@router.post("", response_model=Project)
async def create_project(
    request: CreateProjectRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Create a new project
    
    Creates a new project for the authenticated user.
    """
    user_id = await get_user_id_from_header(authorization)
    
    try:
        project_data = request.model_dump()
        project = await ProjectService.create_project(user_id, project_data)
        return project
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create project error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create project"
        )


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Update a project
    
    Updates project data if owned by the authenticated user.
    """
    user_id = await get_user_id_from_header(authorization)
    
    try:
        project_data = request.model_dump(exclude_none=True)
        project = await ProjectService.update_project(project_id, user_id, project_data)
        return project
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update project error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update project"
        )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Delete a project
    
    Deletes project if owned by the authenticated user.
    """
    user_id = await get_user_id_from_header(authorization)
    
    try:
        result = await ProjectService.delete_project(project_id, user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete project error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete project"
        )

