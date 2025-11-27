"""
Project Service - Handle project operations with Supabase
"""
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import HTTPException
from supabase import create_client, Client

# Load environment variables
load_dotenv()


class ProjectService:
    """Service for handling project operations."""

    @staticmethod
    def get_supabase_client() -> Client:
        """Get Supabase client from environment"""
        url = os.getenv("VITE_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise HTTPException(
                status_code=500,
                detail="Supabase configuration not found"
            )
        
        return create_client(url, key)

    @staticmethod
    async def list_projects(user_id: str) -> List[Dict[str, Any]]:
        """
        List all projects for a user
        
        Args:
            user_id: User's ID
            
        Returns:
            List of projects with metrics
        """
        try:
            supabase = ProjectService.get_supabase_client()
            
            result = supabase.table("impact_projects")\
                .select("*, metrics:project_metrics(*)")\
                .eq("user_id", user_id)\
                .order("display_order")\
                .execute()
            
            projects = []
            for project in result.data:
                # Transform to frontend format
                metrics = []
                if project.get("metrics"):
                    metrics = sorted(project["metrics"], key=lambda m: m.get("display_order", 0))
                    metrics = [
                        {
                            "primary": m["primary_value"],
                            "label": m["label"],
                            "detail": m.get("detail")
                        }
                        for m in metrics
                    ]
                
                projects.append({
                    "id": project["id"],
                    "company": project["company"],
                    "projectName": project["project_name"],
                    "role": project["role"],
                    "teamSize": project["team_size"],
                    "problem": project["problem"],
                    "contributions": project["contributions"] if isinstance(project["contributions"], list) else [project["contributions"]],
                    "techStack": project["tech_stack"],
                    "metrics": metrics
                })
            
            return projects
        except Exception as e:
            print(f"List projects error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch projects"
            )

    @staticmethod
    async def get_project(project_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get a single project
        
        Args:
            project_id: Project ID
            user_id: User's ID (for authorization)
            
        Returns:
            Project data with metrics
        """
        try:
            supabase = ProjectService.get_supabase_client()
            
            result = supabase.table("impact_projects")\
                .select("*, metrics:project_metrics(*)")\
                .eq("id", project_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=404,
                    detail="Project not found"
                )
            
            project = result.data
            
            # Transform metrics
            metrics = []
            if project.get("metrics"):
                metrics = sorted(project["metrics"], key=lambda m: m.get("display_order", 0))
                metrics = [
                    {
                        "primary": m["primary_value"],
                        "label": m["label"],
                        "detail": m.get("detail")
                    }
                    for m in metrics
                ]
            
            return {
                "id": project["id"],
                "company": project["company"],
                "projectName": project["project_name"],
                "role": project["role"],
                "teamSize": project["team_size"],
                "problem": project["problem"],
                "contributions": project["contributions"] if isinstance(project["contributions"], list) else [project["contributions"]],
                "techStack": project["tech_stack"],
                "metrics": metrics
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get project error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch project"
            )

    @staticmethod
    async def create_project(user_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new project
        
        Args:
            user_id: User's ID
            project_data: Project data
            
        Returns:
            Created project data
        """
        try:
            supabase = ProjectService.get_supabase_client()
            
            # Get current project count for display_order
            count_result = supabase.table("impact_projects")\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .execute()
            
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
                        "primary_value": m["primary"],
                        "label": m["label"],
                        "detail": m.get("detail"),
                        "display_order": idx
                    }
                    for idx, m in enumerate(metrics)
                ]
                
                supabase.table("project_metrics")\
                    .insert(metrics_insert)\
                    .execute()
            
            # Return in frontend format
            return {
                "id": project_id,
                "company": project["company"],
                "projectName": project["project_name"],
                "role": project["role"],
                "teamSize": project["team_size"],
                "problem": project["problem"],
                "contributions": project["contributions"] if isinstance(project["contributions"], list) else [project["contributions"]],
                "techStack": project["tech_stack"],
                "metrics": metrics
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Create project error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create project"
            )

    @staticmethod
    async def update_project(project_id: str, user_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a project
        
        Args:
            project_id: Project ID
            user_id: User's ID (for authorization)
            project_data: Project data to update
            
        Returns:
            Updated project data
        """
        try:
            supabase = ProjectService.get_supabase_client()
            
            # Extract metrics if provided
            metrics = project_data.pop("metrics", None)
            
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
                            "primary_value": m["primary"],
                            "label": m["label"],
                            "detail": m.get("detail"),
                            "display_order": idx
                        }
                        for idx, m in enumerate(metrics)
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
            raise HTTPException(
                status_code=500,
                detail="Failed to update project"
            )

    @staticmethod
    async def delete_project(project_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a project
        
        Args:
            project_id: Project ID
            user_id: User's ID (for authorization)
            
        Returns:
            Success message
        """
        try:
            supabase = ProjectService.get_supabase_client()
            
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
            
            return {
                "success": True,
                "message": "Project deleted successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Delete project error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete project"
            )

