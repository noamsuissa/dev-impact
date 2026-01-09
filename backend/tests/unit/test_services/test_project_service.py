"""
Unit tests for ProjectService
Tests business logic with mocked dependencies
"""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from backend.schemas.auth import MessageResponse
from backend.schemas.project import Project, ProjectEvidence, ProjectMetric, StandardizedProjectMetric
from backend.services.project_service import ProjectService


class TestProjectService:
    """Test suite for ProjectService"""

    def test_initialization(self):
        """Test ProjectService initializes correctly"""
        service = ProjectService()
        assert service is not None

    @pytest.mark.asyncio
    async def test_list_projects(self, project_service, mock_supabase_client):
        """Test listing all user projects"""
        # Setup mock
        mock_response = Mock()
        mock_response.data = [
            {
                "id": "project_1",
                "company": "Company 1",
                "project_name": "Project 1",
                "role": "Developer",
                "team_size": 5,
                "problem": "Problem 1",
                "contributions": ["Contrib 1"],
                "tech_stack": ["Python"],
                "portfolio_id": None,
                "metrics": [],
            }
        ]

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = mock_response

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await project_service.list_projects(mock_supabase_client, "user_123")

        # Assert
        assert len(result) == 1
        assert result[0].company == "Company 1"
        assert result[0].projectName == "Project 1"

    @pytest.mark.asyncio
    async def test_list_projects_with_portfolio_filter(self, project_service, mock_supabase_client):
        """Test listing projects filtered by portfolio_id"""
        # Setup mock
        mock_response = Mock()
        mock_response.data = [
            {
                "id": "project_1",
                "company": "Company 1",
                "project_name": "Project 1",
                "role": "Developer",
                "team_size": 5,
                "problem": "Problem 1",
                "contributions": ["Contrib 1"],
                "tech_stack": ["Python"],
                "portfolio_id": "portfolio_123",
                "metrics": [],
            }
        ]

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = mock_response

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await project_service.list_projects(mock_supabase_client, "user_123", portfolio_id="portfolio_123")

        # Assert
        assert len(result) == 1
        assert result[0].portfolio_id == "portfolio_123"

    @pytest.mark.asyncio
    async def test_list_projects_with_evidence(self, project_service, mock_supabase_client):
        """Test listing projects with evidence included"""
        # Setup project mock
        mock_projects = Mock()
        mock_projects.data = [
            {
                "id": "project_1",
                "company": "Company 1",
                "project_name": "Project 1",
                "role": "Developer",
                "team_size": 5,
                "problem": "Problem 1",
                "contributions": ["Contrib 1"],
                "tech_stack": ["Python"],
                "portfolio_id": None,
                "metrics": [],
            }
        ]

        # Setup evidence mock
        mock_evidence = Mock()
        mock_evidence.data = [
            {
                "id": "evidence_1",
                "project_id": "project_1",
                "file_path": "user_123/project_1/file.jpg",
                "file_name": "file.jpg",
                "file_size": 1024,
                "mime_type": "image/jpeg",
                "display_order": 0,
                "created_at": "2024-01-01T00:00:00",
            }
        ]

        mock_projects_query = Mock()
        mock_projects_query.eq.return_value = mock_projects_query
        mock_projects_query.order.return_value = mock_projects_query
        mock_projects_query.execute.return_value = mock_projects

        mock_evidence_query = Mock()
        mock_evidence_query.in_.return_value = mock_evidence_query
        mock_evidence_query.order.return_value = mock_evidence_query
        mock_evidence_query.execute.return_value = mock_evidence

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "project_evidence":
                mock_table.select.return_value = mock_evidence_query
            else:
                mock_table.select.return_value = mock_projects_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        result = await project_service.list_projects(mock_supabase_client, "user_123", include_evidence=True)

        # Assert
        assert len(result) == 1
        assert result[0].evidence is not None
        assert len(result[0].evidence) == 1

    @pytest.mark.asyncio
    async def test_get_project_success(self, project_service, mock_supabase_client):
        """Test getting a single project"""
        # Setup mock
        mock_response = Mock()
        mock_response.data = {
            "id": "project_123",
            "user_id": "user_123",  # Required for access check
            "company": "Company 1",
            "project_name": "Project 1",
            "role": "Developer",
            "team_size": 5,
            "problem": "Problem 1",
            "contributions": ["Contrib 1"],
            "tech_stack": ["Python"],
            "portfolio_id": None,
            "metrics": [],
        }

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.single.return_value = mock_query
        mock_query.execute.return_value = mock_response

        # Mock evidence list - data must be iterable (list)
        # Code does: .select("*").eq("project_id", project_id).order("display_order").execute()
        # No .single() in the chain
        mock_evidence_result = Mock()
        mock_evidence_result.data = []  # Empty list, not None or Mock
        mock_evidence_query = Mock()
        mock_evidence_query.eq.return_value = mock_evidence_query
        mock_evidence_query.order.return_value = mock_evidence_query  # .order(), not .single()
        mock_evidence_query.execute.return_value = mock_evidence_result

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "impact_projects":
                mock_table.select.return_value = mock_query
            elif table_name == "project_evidence":
                mock_table.select.return_value = mock_evidence_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        result = await project_service.get_project(mock_supabase_client, "project_123", "user_123")

        # Assert
        assert isinstance(result, Project)
        assert result.id == "project_123"
        assert result.company == "Company 1"

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, project_service, mock_supabase_client):
        """Test getting project that doesn't exist"""
        # Setup mock - no project found
        mock_response = Mock()
        mock_response.data = None

        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.single.return_value = mock_query
        mock_query.execute.return_value = mock_response

        mock_table = Mock()
        mock_table.select.return_value = mock_query
        mock_supabase_client.table.return_value = mock_table

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await project_service.get_project(mock_supabase_client, "nonexistent", "user_123")

        assert exc_info.value.status_code == 404
        assert "Project not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_project_success(self, project_service, mock_supabase_client, subscription_info):
        """Test creating a project"""
        subscription_info.can_add_project = True

        # Mock count query
        mock_count = Mock()
        mock_count.data = []
        mock_count_query = Mock()
        mock_count_query.select.return_value = mock_count_query
        mock_count_query.eq.return_value = mock_count_query
        mock_count_query.execute.return_value = mock_count

        # Mock insert
        mock_insert = Mock()
        mock_insert.data = [
            {
                "id": "project_123",
                "company": "Company 1",
                "project_name": "Project 1",
                "role": "Developer",
                "team_size": 5,
                "problem": "Problem 1",
                "contributions": ["Contrib 1"],
                "tech_stack": ["Python"],
                "portfolio_id": None,
            }
        ]

        mock_insert_query = Mock()
        mock_insert_query.execute.return_value = mock_insert

        # Mock metrics insert
        mock_metrics_insert = Mock()
        mock_metrics_insert.execute.return_value = Mock()

        mock_table = Mock()
        mock_table.select.return_value = mock_count_query
        mock_table.insert.return_value = mock_insert_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        project_data = {
            "company": "Company 1",
            "projectName": "Project 1",
            "role": "Developer",
            "teamSize": 5,
            "problem": "Problem 1",
            "contributions": ["Contrib 1"],
            "techStack": ["Python"],
            "metrics": [],
        }

        result = await project_service.create_project(mock_supabase_client, subscription_info, "user_123", project_data)

        # Assert
        assert isinstance(result, Project)
        assert result.company == "Company 1"

    @pytest.mark.asyncio
    async def test_create_project_limit_reached(self, project_service, mock_supabase_client, subscription_info):
        """Test project creation when limit is reached"""
        subscription_info.can_add_project = False
        subscription_info.max_projects = 3

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await project_service.create_project(
                mock_supabase_client,
                subscription_info,
                "user_123",
                {
                    "company": "Test",
                    "projectName": "Test",
                    "role": "Dev",
                    "teamSize": 1,
                    "problem": "Test",
                    "contributions": [],
                    "techStack": [],
                },  # noqa: E501
            )

        assert exc_info.value.status_code == 403
        assert "Project limit reached" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_project_standardized_metrics(self, project_service, mock_supabase_client, subscription_info):
        """Test creating project with standardized metrics"""
        subscription_info.can_add_project = True

        # Mock count
        mock_count = Mock()
        mock_count.data = []
        mock_count_query = Mock()
        mock_count_query.select.return_value = mock_count_query
        mock_count_query.eq.return_value = mock_count_query
        mock_count_query.execute.return_value = mock_count

        # Mock insert
        mock_insert = Mock()
        mock_insert.data = [
            {
                "id": "project_123",
                "company": "Company 1",
                "project_name": "Project 1",
                "role": "Developer",
                "team_size": 5,
                "problem": "Problem 1",
                "contributions": ["Contrib 1"],
                "tech_stack": ["Python"],
                "portfolio_id": None,
            }
        ]

        mock_insert_query = Mock()
        mock_insert_query.execute.return_value = mock_insert

        # Mock metrics insert
        mock_metrics_insert = Mock()
        mock_metrics_insert.execute.return_value = Mock()

        mock_table = Mock()
        mock_table.select.return_value = mock_count_query
        mock_table.insert.return_value = mock_insert_query
        mock_supabase_client.table.side_effect = (
            lambda name: mock_table if name == "impact_projects" else Mock(insert=Mock(return_value=mock_metrics_insert))
        )  # noqa: E501

        # Execute with standardized metric
        from backend.schemas.project import PrimaryMetricValue

        metric = StandardizedProjectMetric(type="performance", primary=PrimaryMetricValue(value=50, unit="%", label="faster"))

        project_data = {
            "company": "Company 1",
            "projectName": "Project 1",
            "role": "Developer",
            "teamSize": 5,
            "problem": "Problem 1",
            "contributions": ["Contrib 1"],
            "techStack": ["Python"],
            "metrics": [metric],
        }

        result = await project_service.create_project(mock_supabase_client, subscription_info, "user_123", project_data)

        # Assert
        assert len(result.metrics) == 1
        assert isinstance(result.metrics[0], StandardizedProjectMetric)

    @pytest.mark.asyncio
    async def test_create_project_legacy_metrics(self, project_service, mock_supabase_client, subscription_info):
        """Test creating project with legacy metrics"""
        subscription_info.can_add_project = True

        # Mock count
        mock_count = Mock()
        mock_count.data = []
        mock_count_query = Mock()
        mock_count_query.select.return_value = mock_count_query
        mock_count_query.eq.return_value = mock_count_query
        mock_count_query.execute.return_value = mock_count

        # Mock insert
        mock_insert = Mock()
        mock_insert.data = [
            {
                "id": "project_123",
                "company": "Company 1",
                "project_name": "Project 1",
                "role": "Developer",
                "team_size": 5,
                "problem": "Problem 1",
                "contributions": ["Contrib 1"],
                "tech_stack": ["Python"],
                "portfolio_id": None,
            }
        ]

        mock_insert_query = Mock()
        mock_insert_query.execute.return_value = mock_insert

        # Mock metrics insert
        mock_metrics_insert = Mock()
        mock_metrics_insert.execute.return_value = Mock()

        mock_table = Mock()
        mock_table.select.return_value = mock_count_query
        mock_table.insert.return_value = mock_insert_query
        mock_supabase_client.table.side_effect = (
            lambda name: mock_table if name == "impact_projects" else Mock(insert=Mock(return_value=mock_metrics_insert))
        )  # noqa: E501

        # Execute with legacy metric - use dict format, not ProjectMetric object
        metric = {"primary": "50%", "label": "Performance improvement", "detail": "Reduced load time"}

        project_data = {
            "company": "Company 1",
            "projectName": "Project 1",
            "role": "Developer",
            "teamSize": 5,
            "problem": "Problem 1",
            "contributions": ["Contrib 1"],
            "techStack": ["Python"],
            "metrics": [metric],
        }

        result = await project_service.create_project(mock_supabase_client, subscription_info, "user_123", project_data)

        # Assert
        assert len(result.metrics) == 1
        assert isinstance(result.metrics[0], ProjectMetric)

    @pytest.mark.asyncio
    async def test_update_project(self, project_service, mock_supabase_client):
        """Test updating a project"""
        # Mock update
        mock_update = Mock()
        mock_update.data = [
            {
                "id": "project_123",
                "company": "Updated Company",
                "project_name": "Updated Project",
                "role": "Developer",
                "team_size": 5,
                "problem": "Problem 1",
                "contributions": ["Contrib 1"],
                "tech_stack": ["Python"],
                "portfolio_id": None,
            }
        ]

        mock_update_query = Mock()
        mock_update_query.eq.return_value = mock_update_query
        mock_update_query.execute.return_value = mock_update

        # Mock get_project (called at end of update)
        mock_get = Mock()
        mock_get.data = {
            "id": "project_123",
            "user_id": "user_123",  # Required for access check
            "company": "Updated Company",
            "project_name": "Updated Project",
            "role": "Developer",
            "team_size": 5,
            "problem": "Problem 1",
            "contributions": ["Contrib 1"],
            "tech_stack": ["Python"],
            "portfolio_id": None,
            "metrics": [],
        }

        mock_get_query = Mock()
        mock_get_query.eq.return_value = mock_get_query
        mock_get_query.single.return_value = mock_get_query
        mock_get_query.execute.return_value = mock_get

        # Mock evidence query - data must be iterable (list)
        # Code does: .select("*").eq("project_id", project_id).order("display_order").execute()
        # No .single() in the chain
        mock_evidence_result = Mock()
        mock_evidence_result.data = []  # Empty list, not None or Mock
        mock_evidence_query = Mock()
        mock_evidence_query.eq.return_value = mock_evidence_query
        mock_evidence_query.order.return_value = mock_evidence_query  # .order(), not .single()
        mock_evidence_query.execute.return_value = mock_evidence_result

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "impact_projects":
                mock_table.update.return_value = mock_update_query
                mock_table.select.return_value = mock_get_query
            elif table_name == "project_evidence":
                mock_table.select.return_value = mock_evidence_query
            else:
                mock_table.delete.return_value = Mock(eq=Mock(return_value=Mock(execute=Mock(return_value=Mock()))))
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        project_data = {"company": "Updated Company", "projectName": "Updated Project"}

        result = await project_service.update_project(mock_supabase_client, "project_123", "user_123", project_data)

        # Assert
        assert result.company == "Updated Company"
        assert result.projectName == "Updated Project"

    @pytest.mark.asyncio
    async def test_delete_project(self, project_service, mock_supabase_client):
        """Test deleting a project"""
        # Mock delete
        mock_delete = Mock()
        mock_delete.data = [{"id": "project_123"}]

        mock_delete_query = Mock()
        mock_delete_query.eq.return_value = mock_delete_query
        mock_delete_query.execute.return_value = mock_delete

        mock_table = Mock()
        mock_table.delete.return_value = mock_delete_query
        mock_supabase_client.table.return_value = mock_table

        # Execute
        result = await project_service.delete_project(mock_supabase_client, "project_123", "user_123")

        # Assert
        assert isinstance(result, MessageResponse)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_upload_evidence_file(self, project_service, mock_supabase_client):
        """Test uploading evidence file"""
        # Mock project ownership check
        mock_project = Mock()
        mock_project.data = {"id": "project_123"}

        mock_project_query = Mock()
        mock_project_query.eq.return_value = mock_project_query
        mock_project_query.single.return_value = mock_project_query
        mock_project_query.execute.return_value = mock_project

        # Mock subscription check
        mock_profile = Mock()
        mock_profile.data = {"subscription_type": "free"}

        mock_profile_query = Mock()
        mock_profile_query.eq.return_value = mock_profile_query
        mock_profile_query.single.return_value = mock_profile_query
        mock_profile_query.execute.return_value = mock_profile

        # Mock total size check
        mock_projects_list = Mock()
        mock_projects_list.data = [{"id": "project_123"}]

        mock_projects_query = Mock()
        mock_projects_query.select.return_value = mock_projects_query
        mock_projects_query.eq.return_value = mock_projects_query
        mock_projects_query.execute.return_value = mock_projects_list

        mock_evidence_size = Mock()
        mock_evidence_size.data = []

        mock_evidence_query = Mock()
        mock_evidence_query.select.return_value = mock_evidence_query
        mock_evidence_query.in_.return_value = mock_evidence_query
        mock_evidence_query.execute.return_value = mock_evidence_size

        # Mock existing evidence check
        mock_existing = Mock()
        mock_existing.data = []

        mock_existing_query = Mock()
        mock_existing_query.eq.return_value = mock_existing_query
        mock_existing_query.order.return_value = mock_existing_query
        mock_existing_query.limit.return_value = mock_existing_query
        mock_existing_query.execute.return_value = mock_existing

        # Mock evidence insert
        mock_evidence_insert = Mock()
        mock_evidence_insert.data = [
            {
                "id": "evidence_123",
                "project_id": "project_123",
                "file_path": "user_123/project_123/file.jpg",
                "file_name": "file.jpg",
                "file_size": 1024,
                "mime_type": "image/jpeg",
                "display_order": 0,
                "created_at": "2024-01-01T00:00:00",
            }
        ]

        mock_evidence_insert_query = Mock()
        mock_evidence_insert_query.execute.return_value = mock_evidence_insert

        # Mock storage
        mock_storage_bucket = Mock()
        mock_storage_bucket.upload = Mock()
        mock_storage = Mock()
        mock_storage.from_.return_value = mock_storage_bucket

        # Track calls to return correct query
        call_count = {"impact_projects": 0, "profiles": 0, "project_evidence": 0}

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "impact_projects":
                call_count["impact_projects"] += 1
                if call_count["impact_projects"] == 1:
                    # First call: project ownership check
                    mock_table.select.return_value = mock_project_query
                else:
                    # Second call: get user projects for size calculation
                    mock_table.select.return_value = mock_projects_query
            elif table_name == "profiles":
                mock_table.select.return_value = mock_profile_query
            elif table_name == "project_evidence":
                call_count["project_evidence"] += 1
                if call_count["project_evidence"] == 1:
                    # First call: get evidence sizes
                    mock_table.select.return_value = mock_evidence_query
                elif call_count["project_evidence"] == 2:
                    # Second call: check existing evidence
                    mock_table.select.return_value = mock_existing_query
                else:
                    # Third call: insert evidence
                    mock_table.insert.return_value = mock_evidence_insert_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect
        mock_supabase_client.storage = mock_storage

        # Execute
        result = await project_service.upload_evidence_file(
            mock_supabase_client, "project_123", "user_123", "file.jpg", "image/jpeg", 1024, b"fake image data"
        )

        # Assert
        assert isinstance(result, ProjectEvidence)
        assert result.file_name == "file.jpg"

    @pytest.mark.asyncio
    async def test_upload_evidence_file_size_limit(self, project_service, mock_supabase_client):
        """Test evidence upload when storage limit is reached"""
        # Mock project ownership
        mock_project = Mock()
        mock_project.data = {"id": "project_123"}

        mock_project_query = Mock()
        mock_project_query.eq.return_value = mock_project_query
        mock_project_query.single.return_value = mock_project_query
        mock_project_query.execute.return_value = mock_project

        # Mock subscription (free tier)
        mock_profile = Mock()
        mock_profile.data = {"subscription_type": "free"}

        mock_profile_query = Mock()
        mock_profile_query.eq.return_value = mock_profile_query
        mock_profile_query.single.return_value = mock_profile_query
        mock_profile_query.execute.return_value = mock_profile

        # Mock total size (already at limit)
        mock_projects_list = Mock()
        mock_projects_list.data = [{"id": "project_123"}]

        mock_projects_query = Mock()
        mock_projects_query.select.return_value = mock_projects_query
        mock_projects_query.eq.return_value = mock_projects_query
        mock_projects_query.execute.return_value = mock_projects_list

        # 50MB already used (free tier limit)
        mock_evidence_size = Mock()
        mock_evidence_size.data = [{"file_size": 50 * 1024 * 1024}]

        mock_evidence_query = Mock()
        mock_evidence_query.select.return_value = mock_evidence_query
        mock_evidence_query.in_.return_value = mock_evidence_query
        mock_evidence_query.execute.return_value = mock_evidence_size

        # Track calls to return correct query
        call_count = {"impact_projects": 0}

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "impact_projects":
                call_count["impact_projects"] += 1
                if call_count["impact_projects"] == 1:
                    # First call: project ownership check
                    mock_table.select.return_value = mock_project_query
                else:
                    # Second call: get user projects for size calculation
                    mock_table.select.return_value = mock_projects_query
            elif table_name == "profiles":
                mock_table.select.return_value = mock_profile_query
            elif table_name == "project_evidence":
                mock_table.select.return_value = mock_evidence_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await project_service.upload_evidence_file(
                mock_supabase_client,
                "project_123",
                "user_123",
                "file.jpg",
                "image/jpeg",
                1024 * 1024,  # 1MB
                b"fake image data",
            )

        assert exc_info.value.status_code == 400
        assert "exceed" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_upload_evidence_invalid_mime_type(self, project_service, mock_supabase_client):
        """Test evidence upload with invalid MIME type"""
        # Execute and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await project_service.upload_evidence_file(
                mock_supabase_client, "project_123", "user_123", "file.pdf", "application/pdf", 1024, b"fake pdf data"
            )

        assert exc_info.value.status_code == 400
        assert "image" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_list_project_evidence(self, project_service, mock_supabase_client):
        """Test listing evidence for a project"""
        # Mock project check
        mock_project = Mock()
        mock_project.data = {"user_id": "user_123", "portfolio_id": None}

        mock_project_query = Mock()
        mock_project_query.select.return_value = mock_project_query
        mock_project_query.eq.return_value = mock_project_query
        mock_project_query.single.return_value = mock_project_query
        mock_project_query.execute.return_value = mock_project

        # Mock evidence
        mock_evidence = Mock()
        mock_evidence.data = [
            {
                "id": "evidence_1",
                "project_id": "project_123",
                "file_path": "user_123/project_123/file.jpg",
                "file_name": "file.jpg",
                "file_size": 1024,
                "mime_type": "image/jpeg",
                "display_order": 0,
                "created_at": "2024-01-01T00:00:00",
            }
        ]

        mock_evidence_query = Mock()
        mock_evidence_query.eq.return_value = mock_evidence_query
        mock_evidence_query.order.return_value = mock_evidence_query
        mock_evidence_query.execute.return_value = mock_evidence

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "impact_projects":
                mock_table.select.return_value = mock_project_query
            elif table_name == "project_evidence":
                mock_table.select.return_value = mock_evidence_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        result = await project_service.list_project_evidence(mock_supabase_client, "project_123", "user_123")

        # Assert
        assert len(result) == 1
        assert result[0].file_name == "file.jpg"

    @pytest.mark.asyncio
    async def test_delete_evidence(self, project_service, mock_supabase_client):
        """Test deleting evidence"""
        # Mock evidence with project info
        mock_evidence = Mock()
        mock_evidence.data = {
            "id": "evidence_123",
            "file_path": "user_123/project_123/file.jpg",
            "impact_projects": {"user_id": "user_123"},
        }

        mock_evidence_query = Mock()
        mock_evidence_query.select.return_value = mock_evidence_query
        mock_evidence_query.eq.return_value = mock_evidence_query
        mock_evidence_query.single.return_value = mock_evidence_query
        mock_evidence_query.execute.return_value = mock_evidence

        # Mock delete
        mock_delete = Mock()
        mock_delete.data = [{"id": "evidence_123"}]

        mock_delete_query = Mock()
        mock_delete_query.eq.return_value = mock_delete_query
        mock_delete_query.execute.return_value = mock_delete

        # Mock storage
        mock_storage_bucket = Mock()
        mock_storage_bucket.remove = Mock()
        mock_storage = Mock()
        mock_storage.from_.return_value = mock_storage_bucket

        mock_table = Mock()
        mock_table.select.return_value = mock_evidence_query
        mock_table.delete.return_value = mock_delete_query
        mock_supabase_client.table.return_value = mock_table
        mock_supabase_client.storage = mock_storage

        # Execute
        result = await project_service.delete_evidence(mock_supabase_client, "evidence_123", "user_123")

        # Assert
        assert isinstance(result, MessageResponse)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_get_evidence_stats(self, project_service, mock_supabase_client):
        """Test getting evidence storage statistics"""
        # Mock projects
        mock_projects = Mock()
        mock_projects.data = [{"id": "project_123"}]

        mock_projects_query = Mock()
        mock_projects_query.select.return_value = mock_projects_query
        mock_projects_query.eq.return_value = mock_projects_query
        mock_projects_query.execute.return_value = mock_projects

        # Mock evidence size
        mock_evidence = Mock()
        mock_evidence.data = [{"file_size": 10 * 1024 * 1024}]  # 10MB

        mock_evidence_query = Mock()
        mock_evidence_query.select.return_value = mock_evidence_query
        mock_evidence_query.in_.return_value = mock_evidence_query
        mock_evidence_query.execute.return_value = mock_evidence

        # Mock profile
        mock_profile = Mock()
        mock_profile.data = {"subscription_type": "free"}

        mock_profile_query = Mock()
        mock_profile_query.select.return_value = mock_profile_query
        mock_profile_query.eq.return_value = mock_profile_query
        mock_profile_query.single.return_value = mock_profile_query
        mock_profile_query.execute.return_value = mock_profile

        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "impact_projects":
                mock_table.select.return_value = mock_projects_query
            elif table_name == "project_evidence":
                mock_table.select.return_value = mock_evidence_query
            elif table_name == "profiles":
                mock_table.select.return_value = mock_profile_query
            return mock_table

        mock_supabase_client.table.side_effect = table_side_effect

        # Execute
        result = await project_service.get_evidence_stats(mock_supabase_client, "user_123")

        # Assert
        assert result["total_size_bytes"] == 10 * 1024 * 1024
        assert result["limit_mb"] == 50  # Free tier limit
        assert "percentage_used" in result
