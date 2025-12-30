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
from backend.services.subscription_service import SubscriptionService
from backend.utils import auth_utils
from backend.schemas.auth import MessageResponse
from backend.utils.dependencies import ServiceDBClient

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
)


@router.get("", response_model=List[Project])
async def list_projects(
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token),
    portfolio_id: Optional[str] = Query(None, description="Filter projects by portfolio ID")
):
    """
    List all projects for current user
    
    Returns all projects owned by the authenticated user, optionally filtered by portfolio.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    projects = await ProjectService.list_projects(client, user_id, portfolio_id=portfolio_id)
    return projects


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Get a single project by ID
    
    Returns project data if owned by the authenticated user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    project = await ProjectService.get_project(client, project_id, user_id)
    return project


@router.post("", response_model=Project)
async def create_project(
    request: CreateProjectRequest,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Create a new project
    
    Creates a new project for the authenticated user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    # Step 1: Check subscription limits (orchestration in router)
    subscription_info = await SubscriptionService.get_subscription_info(client, user_id)
    
    # Step 2: Create project
    project_data = request.model_dump()
    project = await ProjectService.create_project(
        client=client,
        subscription_info=subscription_info,
        user_id=user_id,
        project_data=project_data
    )
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Update a project
    
    Updates project data if owned by the authenticated user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    project_data = request.model_dump(exclude_none=True)
    project = await ProjectService.update_project(client, project_id, user_id, project_data)
    return project


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: str,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Delete a project
    
    Deletes project if owned by the authenticated user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    result = await ProjectService.delete_project(client, project_id, user_id)
    return result


@router.get("/{project_id}/evidence", response_model=List[ProjectEvidence])
async def list_project_evidence(
    project_id: str,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    List all evidence for a project.
    Publicly accessible for published profiles.
    Owners can always see their own evidence.
    """
    user_id = None
    if authorization:
        # Try to extract user ID, but don't fail if token is invalid
        try:
            user_id = auth_utils.get_user_id_from_token(authorization.replace("Bearer ", ""))
        except Exception:
            pass  # keep user_id as None for public access
    
    evidence = await ProjectService.list_project_evidence(client, project_id, user_id)
    return evidence


@router.post("/{project_id}/evidence", response_model=ProjectEvidence)
async def upload_project_evidence(
    project_id: str,
    client: ServiceDBClient,
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
        client,
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
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Get user's evidence storage statistics
    
    Returns total evidence size across all projects, limit, and usage percentage.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    stats = await ProjectService.get_evidence_stats(client, user_id)
    return stats


@router.delete("/{project_id}/evidence/{evidence_id}", response_model=MessageResponse)
async def delete_evidence(
    evidence_id: str,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token),
):
    """
    Delete evidence record and file
    
    Deletes evidence record and associated file from storage if owned by the authenticated user.
    """
    user_id = auth_utils.get_user_id_from_authorization(authorization)
    
    result = await ProjectService.delete_evidence(client, evidence_id, user_id)
    return result

