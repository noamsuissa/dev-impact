"""
Project Service - Handle project operations with Supabase
"""
import os
import json
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv
from fastapi import HTTPException
from backend.schemas.project import (
    Project,
    ProjectMetric,
    StandardizedProjectMetric,
    ProjectEvidence,
)
from backend.schemas.auth import MessageResponse
from backend.schemas.subscription import SubscriptionInfoResponse
from supabase import Client
import uuid

# Load environment variables
load_dotenv()


class ProjectService:
    """Service for handling project operations."""
    
    
    def _is_standardized_metric(self, metric: Union[Dict[str, Any], ProjectMetric, StandardizedProjectMetric]) -> bool:
        """Check if a metric is in standardized format"""
        if isinstance(metric, StandardizedProjectMetric):
            return True
        if isinstance(metric, ProjectMetric):
            return False
        if isinstance(metric, dict):
            # Check for standardized fields
            return "type" in metric and "primary" in metric and isinstance(metric.get("primary"), dict)
        return False
    
    
    def _serialize_standardized_metric(self, metric: Union[StandardizedProjectMetric, Dict[str, Any]]) -> Dict[str, Any]:
        """Convert standardized metric to JSONB-compatible dict"""
        if isinstance(metric, StandardizedProjectMetric):
            return metric.model_dump(exclude_none=True)
        return metric
    
    
    def _deserialize_metric(self, db_metric: Dict[str, Any]) -> Union[ProjectMetric, StandardizedProjectMetric]:
        """Convert database metric to Pydantic model"""
        # Check if it's a standardized metric
        if db_metric.get("metric_data") and db_metric.get("metric_type"):
            # Standardized format
            try:
                metric_data = db_metric["metric_data"]
                if isinstance(metric_data, str):
                    metric_data = json.loads(metric_data)
                return StandardizedProjectMetric(**metric_data)
            except Exception as e:
                print(f"Error deserializing standardized metric: {e}")
                # Fallback to legacy if deserialization fails
                pass
        
        # Legacy format
        return ProjectMetric(
            primary=db_metric["primary_value"],
            label=db_metric["label"],
            detail=db_metric.get("detail")
        )

    
    async def list_projects(self, client: Client, user_id: str | None = None, portfolio_id: Optional[str] = None, include_evidence: bool = False) -> List[Project]:
        """
        List all projects for a user, optionally filtered by profile
        
        Args:
            client: Supabase client (injected from router)
            user_id: User's ID
            portfolio_id: Optional profile ID to filter projects
            include_evidence: Whether to include evidence data
            
        Returns:
            List of projects with metrics and optional evidence
        """
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        try:
            query = client.table("impact_projects")\
                .select("*, metrics:project_metrics(*)")\
                .eq("user_id", user_id)
            
            # Filter by portfolio_id if provided
            if portfolio_id:
                query = query.eq("portfolio_id", portfolio_id)
            
            result = query.order("display_order").execute()
            
            # If including evidence, fetch all evidence for these projects
            evidence_map = {}
            if include_evidence and result.data:
                project_ids = [p["id"] for p in result.data]
                evidence_result = client.table("project_evidence")\
                    .select("*")\
                    .in_("project_id", project_ids)\
                    .order("display_order")\
                    .execute()
                
                if evidence_result.data:
                    supabase_url = os.getenv("SUPABASE_URL", "")
                    bucket_name = "project-evidence"
                    
                    for ev in evidence_result.data:
                        pid = ev["project_id"]
                        if pid not in evidence_map:
                            evidence_map[pid] = []
                        
                        # Generate public URL
                        file_path = ev["file_path"]
                        image_url = None
                        if supabase_url and file_path:
                            image_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_path}"
                        
                        evidence_map[pid].append(ProjectEvidence(
                            id=ev["id"],
                            project_id=ev["project_id"],
                            file_path=ev["file_path"],
                            file_name=ev["file_name"],
                            file_size=ev["file_size"],
                            mime_type=ev["mime_type"],
                            display_order=ev["display_order"],
                            created_at=ev["created_at"],
                            url=image_url
                        ))

            projects = []
            for project in result.data:
                # Transform to frontend format
                metrics = []
                if project.get("metrics"):
                    metrics = sorted(project["metrics"], key=lambda m: m.get("display_order", 0))
                    metrics = [
                        self._deserialize_metric(metric)
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
                    portfolio_id=project["portfolio_id"] if "portfolio_id" in project else None,
                    evidence=evidence_map.get(project["id"]) if include_evidence else None
                )
                
                projects.append(project_data)
            
            return projects
        except HTTPException:
            raise
        except Exception as e:
            print(f"List projects error: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch projects")

    
    async def get_project(self, client: Client, project_id: str, user_id: str) -> Project:
        """
        Get a single project
        
        Args:
            client: Supabase client (injected from router)
            project_id: Project ID
            user_id: User's ID (for authorization)
            
        Returns:
            Project data with metrics
        """
        try:
            result = client.table("impact_projects")\
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
                    self._deserialize_metric(metric)
                    for metric in metrics
                ]
            
            # Get evidence for this project
            evidence_list = await self.list_project_evidence(client, project_id, user_id)
            
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
                portfolio_id=project["portfolio_id"] if "portfolio_id" in project else None,
                evidence=evidence_list if evidence_list else None
            )
            
            return project_data
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get project error: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch project")

    
    async def create_project(
        self,
        client: Client,
        subscription_info: SubscriptionInfoResponse,
        user_id: str,
        project_data: Dict[str, Any]
    ) -> Project:
        """
        Create a new project
        
        Args:
            client: Supabase client (injected from router)
            subscription_info: Subscription information
            user_id: User's ID
            project_data: Project data (may include portfolio_id)
            
        Returns:
            Created project
        """
        if not subscription_info.can_add_project:
            raise HTTPException(
                status_code=403,
                detail=f"Project limit reached. Free users are limited to {subscription_info.max_projects} projects. Upgrade to Pro for unlimited projects."
            )
        try:
            # Extract portfolio_id if provided
            portfolio_id = project_data.pop("portfolio_id", None)
            
            # Get current project count for display_order (within profile if specified)
            count_query = client.table("impact_projects")\
                .select("id", count="exact")\
                .eq("user_id", user_id)
            
            if portfolio_id:
                count_query = count_query.eq("portfolio_id", portfolio_id)
            
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
            
            # Add portfolio_id if provided
            if portfolio_id:
                project_insert["portfolio_id"] = portfolio_id
            
            project_result = client.table("impact_projects")\
                .insert(project_insert)\
                .execute()
            
            if not project_result.data:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create project"
                )
            
            project = project_result.data[0]
            project_id = project["id"]
            
            # Insert metrics (handle both legacy and standardized formats)
            if metrics:
                metrics_insert = []
                for idx, metric in enumerate(metrics):
                    if self._is_standardized_metric(metric):
                        # Standardized format
                        metric_data = self._serialize_standardized_metric(metric)
                        metrics_insert.append({
                            "project_id": project_id,
                            "metric_type": metric_data["type"],
                            "metric_data": metric_data,
                            "display_order": idx,
                            # Leave legacy fields as null
                            "primary_value": None,
                            "label": None,
                            "detail": None
                        })
                    else:
                        # Legacy format
                        metrics_insert.append({
                            "project_id": project_id,
                            "primary_value": metric["primary"],
                            "label": metric["label"],
                            "detail": metric.get("detail"),
                            "display_order": idx,
                            # Leave new fields as null
                            "metric_type": None,
                            "metric_data": None
                        })
                
                client.table("project_metrics")\
                    .insert(metrics_insert)\
                    .execute()
            
            # Return in frontend format - use the actual database result which includes portfolio_id
            project_data_result = Project(
                id=project_id,
                company=project["company"],
                projectName=project["project_name"],
                role=project["role"],
                teamSize=project["team_size"],
                problem=project["problem"],
                contributions=project["contributions"] if isinstance(project["contributions"], list) else [project["contributions"]],
                techStack=project["tech_stack"],
                metrics=metrics,
                portfolio_id=project["portfolio_id"] if "portfolio_id" in project else None
            )
            
            return project_data_result
        except HTTPException:
            raise
        except Exception as e:
            print(f"Create project error: {e}")
            raise HTTPException(status_code=500, detail="Failed to create project")

    
    async def update_project(self, client: Client, project_id: str, user_id: str, project_data: Dict[str, Any]) -> Project:
        """
        Update a project
        
        Args:
            client: Supabase client (injected from router)
            project_id: Project ID
            user_id: User's ID (for authorization)
            project_data: Project data to update
            
        Returns:
            Updated project
        """
        try:
            
            # Extract metrics if provided
            metrics = project_data.pop("metrics", None)
            
            # Extract portfolio_id if provided
            portfolio_id = project_data.pop("portfolio_id", None)
            
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
            if portfolio_id is not None:
                update_data["portfolio_id"] = portfolio_id
            
            # Update project if there's data to update
            if update_data:
                project_result = client.table("impact_projects")\
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
                client.table("project_metrics")\
                    .delete()\
                    .eq("project_id", project_id)\
                    .execute()
                
                # Insert new metrics (handle both legacy and standardized formats)
                if metrics:
                    metrics_insert = []
                    for idx, metric in enumerate(metrics):
                        if self._is_standardized_metric(metric):
                            # Standardized format
                            metric_data = self._serialize_standardized_metric(metric)
                            metrics_insert.append({
                                "project_id": project_id,
                                "metric_type": metric_data["type"],
                                "metric_data": metric_data,
                                "display_order": idx,
                                # Leave legacy fields as null
                                "primary_value": None,
                                "label": None,
                                "detail": None
                            })
                        else:
                            # Legacy format
                            metrics_insert.append({
                                "project_id": project_id,
                                "primary_value": metric["primary"],
                                "label": metric["label"],
                                "detail": metric.get("detail"),
                                "display_order": idx,
                                # Leave new fields as null
                                "metric_type": None,
                                "metric_data": None
                            })
                    
                    client.table("project_metrics")\
                        .insert(metrics_insert)\
                        .execute()
            
            # Fetch and return updated project
            return await self.get_project(client, project_id, user_id)
        except HTTPException:
            raise
        except Exception as e:
            print(f"Update project error: {e}")
            raise HTTPException(status_code=500, detail="Failed to update project")

    
    async def delete_project(self, client: Client, project_id: str, user_id: str) -> MessageResponse:
        """
        Delete a project
        
        Args:
            client: Supabase client (injected from router)
            project_id: Project ID
            user_id: User's ID (for authorization)
            
        Returns:
            MessageResponse with success status
        """
        try:
            # Delete project (metrics will be cascade deleted if FK is set up correctly)
            result = client.table("impact_projects")\
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

    
    async def get_user_total_evidence_size(self, client: Client, user_id: str) -> int:
        """
        Get total size of all evidence for a user across all projects
        
        Args:
            client: Supabase client (injected from router)
            user_id: User's ID
            
        Returns:
            Total size in bytes
        """
        try:
            # Get all projects for user
            projects_result = client.table("impact_projects")\
                .select("id")\
                .eq("user_id", user_id)\
                .execute()
            
            if not projects_result.data:
                return 0
            
            project_ids = [p["id"] for p in projects_result.data]
            
            # Get sum of file sizes for all evidence
            evidence_result = client.table("project_evidence")\
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

    
    async def list_project_evidence(self, client: Client, project_id: str, user_id: Optional[str] = None) -> List[ProjectEvidence]:
        """
        List all evidence for a project
        
        Args:
            client: Supabase client (injected from router)
            project_id: Project ID
            user_id: User's ID (for authorization) or None for public access check
            
        Returns:
            List of evidence items
        """
        try:
            # Fetch project details to determine access
            proj_query = client.table("impact_projects")\
                .select("user_id, portfolio_id")\
                .eq("id", project_id)\
                .single()
            
            proj_result = proj_query.execute()
            
            if not proj_result.data:
                raise HTTPException(status_code=404, detail="Project not found")
            
            project_data = proj_result.data
            owner_id = project_data["user_id"]
            portfolio_id = project_data.get("portfolio_id")
            
            # Determine if user has access
            has_access = False
            
            # 1. Access granted if user is owner
            if user_id and user_id == owner_id:
                has_access = True
            
            # 2. Access granted if project is published (skip if already granted)
            if not has_access:
                # Check published_profiles
                pub_query = client.table("published_profiles")\
                    .select("id")\
                    .eq("is_published", True)
                
                if portfolio_id:
                    # Specific profile check
                    pub_query = pub_query.eq("portfolio_id", portfolio_id)
                else:
                    # Legacy/Default fallback: check if user has ANY published profile
                    pub_query = pub_query.eq("user_id", owner_id)
                
                pub_result = pub_query.limit(1).execute()
                if pub_result.data:
                    has_access = True
            
            if not has_access:
                raise HTTPException(status_code=404, detail="Project not found or access denied")
            
            return await self._fetch_evidence_list(client, project_id)
        except HTTPException:
            raise
        except Exception as e:
            print(f"List project evidence error: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch evidence")

    
    async def _fetch_evidence_list(self, client: Client, project_id: str) -> List[ProjectEvidence]:
        """
        Fetch evidence list for a project
        
        Args:
            client: Supabase client (injected from router)
            project_id: Project ID
            
        Returns:
            List of evidence items
        """
        try:
            # Get evidence
            evidence_result = client.table("project_evidence")\
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

    
    async def upload_evidence_file(
        self,
        client: Client,
        project_id: str,
        user_id: str,
        file_name: str,
        mime_type: str,
        file_size: int,
        file_content: bytes,
    ) -> ProjectEvidence:
        """
        Upload evidence file to Supabase storage and create evidence record.
        
        Args:
            client: Supabase client (injected from router)
            project_id: Project ID
            user_id: User's ID (for authorization)
            file_name: Name of the file
            mime_type: MIME type of the file
            file_size: Size of the file in bytes
            file_content: Binary content of the file
            
        Returns:
            ProjectEvidence with the uploaded file details
        """
        try:
            # Validate mime type is image
            if not mime_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Only image files are allowed")

            # Verify project ownership
            project_result = client.table("impact_projects")\
                .select("id")\
                .eq("id", project_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()

            if not project_result.data:
                raise HTTPException(status_code=404, detail="Project not found")

            # Check user's total size limit based on subscription
            # Get user's subscription type
            profile_result = client.table("profiles")\
                .select("subscription_type")\
                .eq("id", user_id)\
                .single()\
                .execute()
            
            subscription_type = profile_result.data.get("subscription_type", "free") if profile_result.data else "free"
            
            # Set limit based on subscription
            if subscription_type == "pro":
                max_size_mb = int(os.getenv("PRO_MAX_USER_EVIDENCE_SIZE_MB", "5120"))
            else:
                max_size_mb = int(os.getenv("FREE_MAX_USER_EVIDENCE_SIZE_MB", "50"))
            
            max_size_bytes = max_size_mb * 1024 * 1024

            current_total = await self.get_user_total_evidence_size(client, user_id)
            if current_total + file_size > max_size_bytes:
                used_mb = current_total / (1024 * 1024)
                max_mb = max_size_mb
                plan_name = "Pro" if subscription_type == "pro" else "free"
                raise HTTPException(
                    status_code=400,
                    detail=f"Upload would exceed {plan_name} plan storage limit. Current: {used_mb:.2f} MB / {max_mb} MB across all projects"
                )

            # Generate unique file path
            file_extension = file_name.split('.')[-1] if '.' in file_name else ''
            unique_file_name = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            file_path = f"{user_id}/{project_id}/{unique_file_name}"

            # Upload file to Supabase storage
            try:
                client.storage.from_("project-evidence").upload(
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
            existing_evidence = client.table("project_evidence")\
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

            evidence_result = client.table("project_evidence")\
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

    
    async def delete_evidence(self, client: Client, evidence_id: str, user_id: str) -> MessageResponse:
        """
        Delete evidence record and file from storage
        
        Args:
            client: Supabase client (injected from router)
            evidence_id: Evidence ID
            user_id: User's ID (for authorization)
            
        Returns:
            MessageResponse with success status
        """
        try:
            # Get evidence with project info to verify ownership
            evidence_result = client.table("project_evidence")\
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
                client.storage.from_("project-evidence").remove([file_path])
            except Exception as storage_error:
                print(f"Storage delete error (continuing with DB delete): {storage_error}")
            
            # Delete evidence record
            delete_result = client.table("project_evidence")\
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

    
    async def get_evidence_stats(self, client: Client, user_id: str) -> dict:
        """
        Get evidence storage statistics for a user
        
        Args:
            client: Supabase client (injected from router)
            user_id: User's ID
            
        Returns:
            Dictionary with total_size_bytes, limit_bytes, total_size_mb, limit_mb, percentage_used
        """
        try:
            # Get total size across all projects
            total_size_bytes = await self.get_user_total_evidence_size(client, user_id)
            
            # Get user's subscription type
            profile_result = client.table("profiles")\
                .select("subscription_type")\
                .eq("id", user_id)\
                .single()\
                .execute()
            
            subscription_type = profile_result.data.get("subscription_type", "free") if profile_result.data else "free"
            
            # Set limit based on subscription
            if subscription_type == "pro":
                limit_mb = int(os.getenv("PRO_MAX_USER_EVIDENCE_SIZE_MB", "5120"))
            else:
                limit_mb = int(os.getenv("FREE_MAX_USER_EVIDENCE_SIZE_MB", "50"))
            
            limit_bytes = limit_mb * 1024 * 1024
            
            # Calculate percentage
            percentage_used = (total_size_bytes / limit_bytes * 100) if limit_bytes > 0 else 0
            
            return {
                "total_size_bytes": total_size_bytes,
                "limit_bytes": limit_bytes,
                "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
                "limit_mb": limit_mb,
                "percentage_used": round(percentage_used, 2)
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get evidence stats error: {e}")
            raise HTTPException(status_code=500, detail="Failed to get evidence stats")
