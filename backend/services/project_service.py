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
)
from schemas.auth import MessageResponse

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

