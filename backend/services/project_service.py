"""
Project Service - Handle project operations with Supabase
"""
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import HTTPException
from utils.auth_utils import get_supabase_client
from schemas.project import (
    Project,
    ProjectMetric,
    ProjectEvidence,
)
from schemas.auth import MessageResponse
import uuid

# Load environment variables
load_dotenv()


class ProjectService:
    """Service for handling project operations."""

    @staticmethod
    async def list_projects(user_id: str, profile_id: Optional[str] = None) -> List[Project]:
        """
        List all projects for a user, optionally filtered by profile
        
        Args:
            user_id: User's ID
            profile_id: Optional profile ID to filter projects
            
        Returns:
            List of projects with metrics
        """
        try:
            supabase = get_supabase_client()
            
            query = supabase.table("impact_projects")\
                .select("*, metrics:project_metrics(*)")\
                .eq("user_id", user_id)
            
            # Filter by profile_id if provided
            if profile_id:
                query = query.eq("profile_id", profile_id)
            
            result = query.order("display_order").execute()
            
            projects = []
            for project in result.data:
                # Transform to frontend format
                metrics = []
                if project.get("metrics"):
                    metrics = sorted(project["metrics"], key=lambda m: m.get("display_order", 0))
                    metrics = [
                        ProjectMetric(
                            primary=metric["primary_value"],
                            label=metric["label"],
                            detail=metric.get("detail")
                        )
                        for metric in metrics
                    ]
                
                project_data = Project(
                    id=project["id"],
                    company=project["company"],
                    projectName=project["project_name"],
                    role=project["role"],
                    teamSize=project["team_size"],
                    problem=project["problem"],
                    contributions=project["contributions"] if isinstance(project["contributions"], list) else [project["contributions"]],
                    techStack=project["tech_stack"],
                    metrics=metrics,
                    profile_id=project["profile_id"] if "profile_id" in project else None
                )
                
                projects.append(project_data)
            
            return projects
        except HTTPException:
            raise
        except Exception as e:
            print(f"List projects error: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch projects")

    @staticmethod
    async def get_project(project_id: str, user_id: str) -> Project:
        """
        Get a single project
        
        Args:
            project_id: Project ID
            user_id: User's ID (for authorization)
            
        Returns:
            Project data with metrics
        """
        try:
            supabase = get_supabase_client()
            
            result = supabase.table("impact_projects")\
                .select("*, metrics:project_metrics(*)")\
                .eq("id", project_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Project not found")
            
            project = result.data
            
            # Transform metrics
            metrics = []
            if project.get("metrics"):
                metrics = sorted(project["metrics"], key=lambda m: m.get("display_order", 0))
                metrics = [
                    ProjectMetric(
                        primary=metric["primary_value"],
                        label=metric["label"],
                        detail=metric.get("detail")
                    )
                    for metric in metrics
                ]
            
            # Get evidence for this project
            evidence_list = await ProjectService.list_project_evidence(project_id, user_id)
            
            project_data = Project(
                id=project["id"],
                company=project["company"],
                projectName=project["project_name"],
                role=project["role"],
                teamSize=project["team_size"],
                problem=project["problem"],
                contributions=project["contributions"] if isinstance(project["contributions"], list) else [project["contributions"]],
                techStack=project["tech_stack"],
                metrics=metrics,
                profile_id=project["profile_id"] if "profile_id" in project else None,
                evidence=evidence_list if evidence_list else None
            )
            
            return project_data
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get project error: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch project")

    @staticmethod
    async def create_project(user_id: str, project_data: Dict[str, Any]) -> Project:
        """
        Create a new project
        
        Args:
            user_id: User's ID
            project_data: Project data (may include profile_id)
            
        Returns:
            Created project
        """
        try:
            supabase = get_supabase_client()
            
            # Extract profile_id if provided
            profile_id = project_data.pop("profile_id", None)
            
            # Get current project count for display_order (within profile if specified)
            count_query = supabase.table("impact_projects")\
                .select("id", count="exact")\
                .eq("user_id", user_id)
            
            if profile_id:
                count_query = count_query.eq("profile_id", profile_id)
            
            count_result = count_query.execute()
            
            display_order = len(count_result.data) if count_result.data else 0
            
            # Extract metrics from project data
            metrics = project_data.pop("metrics", [])
            
            # Insert project
            project_insert = {
                "user_id": user_id,
                "company": project_data["company"],
                "project_name": project_data["projectName"],
                "role": project_data["role"],
                "team_size": project_data["teamSize"],
                "problem": project_data["problem"],
                "contributions": project_data["contributions"],
                "tech_stack": project_data["techStack"],
                "display_order": display_order
            }
            
            # Add profile_id if provided
            if profile_id:
                project_insert["profile_id"] = profile_id
            
            project_result = supabase.table("impact_projects")\
                .insert(project_insert)\
                .execute()
            
            if not project_result.data:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create project"
                )
            
            project = project_result.data[0]
            project_id = project["id"]
            
            # Insert metrics
            if metrics:
                metrics_insert = [
                    {
                        "project_id": project_id,
                        "primary_value": metric["primary"],
                        "label": metric["label"],
                        "detail": metric.get("detail"),
                        "display_order": idx
                    }
                    for idx, metric in enumerate(metrics)
                ]
                
                supabase.table("project_metrics")\
                    .insert(metrics_insert)\
                    .execute()
            
            # Return in frontend format - use the actual database result which includes profile_id
            project_data = Project(
                id=project_id,
                company=project["company"],
                projectName=project["project_name"],
                role=project["role"],
                teamSize=project["team_size"],
                problem=project["problem"],
                contributions=project["contributions"] if isinstance(project["contributions"], list) else [project["contributions"]],
                techStack=project["tech_stack"],
                metrics=metrics,
                profile_id=project["profile_id"] if "profile_id" in project else None
            )
            
            return project_data
        except HTTPException:
            raise
        except Exception as e:
            print(f"Create project error: {e}")
            raise HTTPException(status_code=500, detail="Failed to create project")

    @staticmethod
    async def update_project(project_id: str, user_id: str, project_data: Dict[str, Any]) -> Project:
        """
        Update a project
        
        Args:
            project_id: Project ID
            user_id: User's ID (for authorization)
            project_data: Project data to update
            
        Returns:
            Updated project
        """
        try:
            supabase = get_supabase_client()
            
            # Extract metrics if provided
            metrics = project_data.pop("metrics", None)
            
            # Extract profile_id if provided
            profile_id = project_data.pop("profile_id", None)
            
            # Prepare update data (convert frontend keys to backend keys)
            update_data = {}
            if "company" in project_data:
                update_data["company"] = project_data["company"]
            if "projectName" in project_data:
                update_data["project_name"] = project_data["projectName"]
            if "role" in project_data:
                update_data["role"] = project_data["role"]
            if "teamSize" in project_data:
                update_data["team_size"] = project_data["teamSize"]
            if "problem" in project_data:
                update_data["problem"] = project_data["problem"]
            if "contributions" in project_data:
                update_data["contributions"] = project_data["contributions"]
            if "techStack" in project_data:
                update_data["tech_stack"] = project_data["techStack"]
            if profile_id is not None:
                update_data["profile_id"] = profile_id
            
            # Update project if there's data to update
            if update_data:
                project_result = supabase.table("impact_projects")\
                    .update(update_data)\
                    .eq("id", project_id)\
                    .eq("user_id", user_id)\
                    .execute()
                
                if not project_result.data:
                    raise HTTPException(
                        status_code=404,
                        detail="Project not found"
                    )
            
            # Update metrics if provided
            if metrics is not None:
                # Delete old metrics
                supabase.table("project_metrics")\
                    .delete()\
                    .eq("project_id", project_id)\
                    .execute()
                
                # Insert new metrics
                if metrics:
                    metrics_insert = [
                        {
                            "project_id": project_id,
                            "primary_value": metric["primary"],
                            "label": metric["label"],
                            "detail": metric.get("detail"),
                            "display_order": idx
                        }
                        for idx, metric in enumerate(metrics)
                    ]
                    
                    supabase.table("project_metrics")\
                        .insert(metrics_insert)\
                        .execute()
            
            # Fetch and return updated project
            return await ProjectService.get_project(project_id, user_id)
        except HTTPException:
            raise
        except Exception as e:
            print(f"Update project error: {e}")
            raise HTTPException(status_code=500, detail="Failed to update project")

    @staticmethod
    async def delete_project(project_id: str, user_id: str) -> MessageResponse:
        """
        Delete a project
        
        Args:
            project_id: Project ID
            user_id: User's ID (for authorization)
            
        Returns:
            MessageResponse with success status
        """
        try:
            supabase = get_supabase_client()
            
            # Delete project (metrics will be cascade deleted if FK is set up correctly)
            result = supabase.table("impact_projects")\
                .delete()\
                .eq("id", project_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=404,
                    detail="Project not found"
                )
            
            return MessageResponse(success=True, message="Project deleted successfully")
        except HTTPException:
            raise
        except Exception as e:
            print(f"Delete project error: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete project")

    @staticmethod
    async def get_user_total_evidence_size(user_id: str) -> int:
        """
        Get total size of all evidence for a user across all projects
        
        Args:
            user_id: User's ID
            
        Returns:
            Total size in bytes
        """
        try:
            supabase = get_supabase_client()
            
            # Get all projects for user
            projects_result = supabase.table("impact_projects")\
                .select("id")\
                .eq("user_id", user_id)\
                .execute()
            
            if not projects_result.data:
                return 0
            
            project_ids = [p["id"] for p in projects_result.data]
            
            # Get sum of file sizes for all evidence
            evidence_result = supabase.table("project_evidence")\
                .select("file_size")\
                .in_("project_id", project_ids)\
                .execute()
            
            total_size = sum(e.get("file_size", 0) for e in evidence_result.data) if evidence_result.data else 0
            return total_size
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get user total evidence size error: {e}")
            raise HTTPException(status_code=500, detail="Failed to calculate total evidence size")

    @staticmethod
    async def list_project_evidence(project_id: str, user_id: str) -> List[ProjectEvidence]:
        """
        List all evidence for a project
        
        Args:
            project_id: Project ID
            user_id: User's ID (for authorization)
            
        Returns:
            List of evidence items
        """
        try:
            supabase = get_supabase_client()
            
            # Verify project ownership
            project_result = supabase.table("impact_projects")\
                .select("id")\
                .eq("id", project_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not project_result.data:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Get evidence
            evidence_result = supabase.table("project_evidence")\
                .select("*")\
                .eq("project_id", project_id)\
                .order("display_order")\
                .execute()
            
            evidence_list = []
            if evidence_result.data:
                supabase_url = os.getenv("SUPABASE_URL", "")
                bucket_name = "project-evidence"
                
                for evidence in evidence_result.data:
                    # Generate public URL for the image
                    file_path = evidence["file_path"]
                    image_url = None
                    if supabase_url and file_path:
                        image_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_path}"
                    
                    evidence_list.append(ProjectEvidence(
                        id=evidence["id"],
                        project_id=evidence["project_id"],
                        file_path=evidence["file_path"],
                        file_name=evidence["file_name"],
                        file_size=evidence["file_size"],
                        mime_type=evidence["mime_type"],
                        display_order=evidence["display_order"],
                        created_at=evidence["created_at"],
                        url=image_url
                    ))
            
            return evidence_list
        except HTTPException:
            raise
        except Exception as e:
            print(f"List project evidence error: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch evidence")

    @staticmethod
    async def upload_evidence_file(
        project_id: str,
        user_id: str,
        file_name: str,
        mime_type: str,
        file_size: int,
        file_content: bytes,
    ) -> ProjectEvidence:
        """
        Upload evidence file to Supabase storage and create evidence record.
        """
        try:
            # Validate mime type is image
            if not mime_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Only image files are allowed")

            # Verify project ownership
            supabase = get_supabase_client()
            project_result = supabase.table("impact_projects")\
                .select("id")\
                .eq("id", project_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()

            if not project_result.data:
                raise HTTPException(status_code=404, detail="Project not found")

            # Check user's total size limit
            max_size_mb = int(os.getenv("MAX_USER_EVIDENCE_SIZE_MB", "50"))
            max_size_bytes = max_size_mb * 1024 * 1024

            current_total = await ProjectService.get_user_total_evidence_size(user_id)
            if current_total + file_size > max_size_bytes:
                used_mb = current_total / (1024 * 1024)
                max_mb = max_size_mb
                raise HTTPException(
                    status_code=400,
                    detail=f"Upload would exceed size limit. Current: {used_mb:.2f} MB / {max_mb} MB"
                )

            # Generate unique file path
            file_extension = file_name.split('.')[-1] if '.' in file_name else ''
            unique_file_name = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            file_path = f"{user_id}/{project_id}/{unique_file_name}"

            # Upload file to Supabase storage
            try:
                supabase.storage.from_("project-evidence").upload(
                    file_path,
                    file_content,
                    file_options={
                        "content-type": mime_type,
                        "upsert": "false"
                    }
                )
            except Exception as e:
                print(f"Storage upload error: {e}")
                raise HTTPException(status_code=500, detail="Failed to upload file to storage")

            # Get current max display_order for this project
            existing_evidence = supabase.table("project_evidence")\
                .select("display_order")\
                .eq("project_id", project_id)\
                .order("display_order", desc=True)\
                .limit(1)\
                .execute()

            display_order = 0
            if existing_evidence.data:
                max_order = existing_evidence.data[0].get("display_order", -1)
                display_order = max_order + 1

            # Create evidence record
            evidence_insert = {
                "project_id": project_id,
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size,
                "mime_type": mime_type,
                "display_order": display_order
            }

            evidence_result = supabase.table("project_evidence")\
                .insert(evidence_insert)\
                .execute()

            if not evidence_result.data:
                raise HTTPException(status_code=500, detail="Failed to create evidence record")

            evidence = evidence_result.data[0]

            # Generate public URL for the image
            supabase_url = os.getenv("SUPABASE_URL", "")
            bucket_name = "project-evidence"
            image_url = None
            if supabase_url and file_path:
                image_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_path}"

            return ProjectEvidence(
                id=evidence["id"],
                project_id=evidence["project_id"],
                file_path=evidence["file_path"],
                file_name=evidence["file_name"],
                file_size=evidence["file_size"],
                mime_type=evidence["mime_type"],
                display_order=evidence["display_order"],
                created_at=evidence["created_at"],
                url=image_url
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Upload evidence file error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload evidence file")

    @staticmethod
    async def delete_evidence(evidence_id: str, user_id: str) -> MessageResponse:
        """
        Delete evidence record and file from storage
        
        Args:
            evidence_id: Evidence ID
            user_id: User's ID (for authorization)
            
        Returns:
            MessageResponse with success status
        """
        try:
            supabase = get_supabase_client()
            
            # Get evidence with project info to verify ownership
            evidence_result = supabase.table("project_evidence")\
                .select("*, impact_projects!inner(user_id)")\
                .eq("id", evidence_id)\
                .eq("impact_projects.user_id", user_id)\
                .single()\
                .execute()
            
            if not evidence_result.data:
                raise HTTPException(status_code=404, detail="Evidence not found")
            
            evidence = evidence_result.data
            file_path = evidence["file_path"]
            
            # Delete file from storage
            try:
                supabase.storage.from_("project-evidence").remove([file_path])
            except Exception as storage_error:
                print(f"Storage delete error (continuing with DB delete): {storage_error}")
            
            # Delete evidence record
            delete_result = supabase.table("project_evidence")\
                .delete()\
                .eq("id", evidence_id)\
                .execute()
            
            if not delete_result.data:
                raise HTTPException(status_code=404, detail="Evidence not found")
            
            return MessageResponse(success=True, message="Evidence deleted successfully")
        except HTTPException:
            raise
        except Exception as e:
            print(f"Delete evidence error: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete evidence")
