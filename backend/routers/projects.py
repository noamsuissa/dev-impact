"""
Projects Router - Handle project CRUD endpoints
"""
from fastapi import APIRouter, Query, Depends, UploadFile, File, Header
from typing import Optional, List
from backend.schemas.project import (
    Project,
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectEvidence,
    EvidenceStatsResponse,
)
from backend.services.project_service import ProjectService
from backend.utils import auth_utils
from backend.schemas.auth import MessageResponse

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


@router.get("/{project_id}/evidence", response_model=List[ProjectEvidence])
async def list_project_evidence(
    project_id: str,
):
    """
    List all evidence for a project
    
    Returns all evidence items for the project.
    Publicly accessible for published profiles.
    """
    # Public access check handled by service (user_id=None)
    evidence = await ProjectService.list_project_evidence(project_id, None)
    return evidence


@router.post("/{project_id}/evidence", response_model=ProjectEvidence)
async def upload_project_evidence(
    project_id: str,
    file: UploadFile = File(...),
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Upload a screenshot for a project and create an evidence record.

    Accepts an image file upload, validates it, uploads to Supabase storage,
    and creates the evidence record in a single step.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)

    file_content = await file.read()
    file_size = len(file_content)

    evidence = await ProjectService.upload_evidence_file(
        project_id=project_id,
        user_id=user_id,
        file_name=file.filename or "screenshot",
        mime_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        file_content=file_content,
    )

    return evidence


@router.get("/evidence/stats", response_model=EvidenceStatsResponse)
async def get_evidence_stats(
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Get user's evidence storage statistics
    
    Returns total evidence size across all projects, limit, and usage percentage.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    stats = await ProjectService.get_evidence_stats(user_id)
    return stats


@router.delete("/{project_id}/evidence/{evidence_id}", response_model=MessageResponse)
async def delete_evidence(
    project_id: str,
    evidence_id: str,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Delete evidence record and file
    
    Deletes evidence record and associated file from storage if owned by the authenticated user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    result = await ProjectService.delete_evidence(evidence_id, user_id)
    return result

