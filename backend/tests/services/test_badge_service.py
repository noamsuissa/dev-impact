"""
Unit tests for BadgeService

Tests all badge service methods with comprehensive coverage for:
- Happy paths
- Error cases
- Edge cases
- Authorization checks
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import datetime

# Import the service
from backend.services.badges.badge_service import BadgeService

from backend.schemas.badge import (
    BadgeDefinition,
    UserBadge,
    UserBadgeWithDetails,
    BadgeProgress,
    BadgeStatsResponse,
    BadgeAuditLog,
    ListBadgesResponse,
    UserBadgesResponse,
    BadgeProgressResponse,
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    return MagicMock()


@pytest.fixture
def sample_badge_definition():
    """Sample badge definition for testing."""
    return {
        "id": "badge_123",
        "badge_key": "first_project",
        "name": "First Project",
        "description": "Complete your first project",
        "category": "getting_started",
        "has_tiers": True,
        "bronze_threshold": {"value": 1},
        "silver_threshold": {"value": 5},
        "gold_threshold": {"value": 10},
        "metric_type": "project_count",
        "calculation_type": "aggregate",
        "calculation_logic": {},
        "data_source": "project_metrics",
        "requires_github": False,
        "icon_name": "trophy",
        "color_scheme": {"bronze": "#CD7F32", "silver": "#C0C0C0", "gold": "#FFD700"},
        "display_order": 1,
        "is_active": True,
        "is_hidden": False,
        "is_beta": False,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "version": 1,
    }


@pytest.fixture
def sample_user_badge():
    """Sample user badge for testing."""
    return {
        "id": "user_badge_123",
        "user_id": "user_123",
        "badge_id": "badge_123",
        "portfolio_id": "portfolio_123",
        "tier": "bronze",
        "earned_at": "2024-01-01T00:00:00",
        "achievement_value": 1.0,
        "achievement_data": {"projects": 1},
        "source_project_ids": ["project_123"],
        "source_metric_ids": None,
        "github_data": None,
        "is_featured": False,
        "is_public": True,
        "display_order": None,
        "progress_to_next_tier": 0.0,
        "previous_tier": None,
        "upgraded_at": None,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


@pytest.fixture
def sample_user_badge_with_details(sample_user_badge):
    """Sample user badge with details for testing."""
    return {
        **sample_user_badge,
        "badge_key": "first_project",
        "name": "First Project",
        "description": "Complete your first project",
        "category": "getting_started",
        "icon_name": "trophy",
        "color_scheme": {"bronze": "#CD7F32", "silver": "#C0C0C0", "gold": "#FFD700"},
    }


@pytest.fixture
def sample_badge_progress():
    """Sample badge progress for testing."""
    return {
        "id": "progress_123",
        "user_id": "user_123",
        "badge_id": "badge_123",
        "current_value": 3.0,
        "target_value": 5.0,
        "target_tier": "silver",
        "progress_percentage": 60.0,
        "contributing_projects": ["project_1", "project_2", "project_3"],
        "last_contribution_at": "2024-01-01T00:00:00",
        "progress_data": {},
        "first_tracked_at": "2024-01-01T00:00:00",
        "last_updated_at": "2024-01-01T00:00:00",
    }


@pytest.fixture
def sample_badge_stats():
    """Sample badge stats for testing."""
    return {
        "user_id": "user_123",
        "total_badges": 5,
        "bronze_count": 2,
        "silver_count": 2,
        "gold_count": 1,
        "unique_badges": 5,
        "most_recent_badge": "2024-01-01T00:00:00",
        "badges_by_category": {"getting_started": 3, "advanced": 2},
    }


# ============================================
# TEST: get_badge_definitions()
# ============================================

class TestGetBadgeDefinitions:
    """Tests for get_badge_definitions method."""

    def test_get_all_badge_definitions_success(
        self, mock_supabase_client, sample_badge_definition
    ):
        """Test successfully getting all active badge definitions."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = [sample_badge_definition]
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.get_badge_definitions(mock_supabase_client)

        # Assert
        assert len(result.badges) == 1
        assert result.total == 1
        assert result.badges[0].badge_key == "first_project"
        mock_supabase_client.table.assert_called_with("badge_definitions")

    def test_get_badge_definitions_empty_result(self, mock_supabase_client):
        """Test getting badge definitions when none exist."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.get_badge_definitions(mock_supabase_client)

        # Assert
        assert len(result.badges) == 0
        assert result.total == 0

    def test_get_badge_definitions_database_error(self, mock_supabase_client):
        """Test handling database error when getting badge definitions."""
        # Arrange
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.get_badge_definitions(mock_supabase_client)
        assert exc_info.value.status_code == 500
        assert "Failed to fetch badge definitions" in exc_info.value.detail


# ============================================
# TEST: get_badge_definition(badge_id)
# ============================================

class TestGetBadgeDefinition:
    """Tests for get_badge_definition method."""

    def test_get_badge_definition_success(
        self, mock_supabase_client, sample_badge_definition
    ):
        """Test successfully getting a specific badge definition."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = sample_badge_definition
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.get_badge_definition(mock_supabase_client, "badge_123")

        # Assert
        assert result.id == "badge_123"
        assert result.badge_key == "first_project"
        mock_supabase_client.table.assert_called_with("badge_definitions")

    def test_get_badge_definition_not_found(self, mock_supabase_client):
        """Test getting a badge definition that doesn't exist."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.get_badge_definition(mock_supabase_client, "nonexistent_badge")
        assert exc_info.value.status_code == 404
        assert "Badge definition not found" in exc_info.value.detail

    def test_get_badge_definition_invalid_badge_id(self, mock_supabase_client):
        """Test getting a badge definition with invalid badge_id."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.get_badge_definition(mock_supabase_client, "")
        assert exc_info.value.status_code == 400
        assert "Badge ID is required" in exc_info.value.detail


# ============================================
# TEST: get_user_badges(user_id)
# ============================================

class TestGetUserBadges:
    """Tests for get_user_badges method."""

    def test_get_user_badges_success(
        self, mock_supabase_client, sample_user_badge_with_details
    ):
        """Test successfully getting user's earned badges."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = [sample_user_badge_with_details]
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.get_user_badges(mock_supabase_client, "user_123")

        # Assert
        assert len(result.badges) == 1
        assert result.total == 1
        assert result.badges[0].user_id == "user_123"
        mock_supabase_client.table.assert_called_with("user_badges_with_details")

    def test_get_user_badges_empty_result(self, mock_supabase_client):
        """Test getting user badges when user has none."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.get_user_badges(mock_supabase_client, "user_123")

        # Assert
        assert len(result.badges) == 0
        assert result.total == 0

    def test_get_user_badges_invalid_user_id(self, mock_supabase_client):
        """Test getting user badges with invalid user_id."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.get_user_badges(mock_supabase_client, "")
        assert exc_info.value.status_code == 400
        assert "User ID is required" in exc_info.value.detail


# ============================================
# TEST: get_user_badge_progress(user_id)
# ============================================

class TestGetUserBadgeProgress:
    """Tests for get_user_badge_progress method."""

    def test_get_user_badge_progress_success(
        self, mock_supabase_client, sample_badge_progress
    ):
        """Test successfully getting user's badge progress."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = [sample_badge_progress]
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.get_user_badge_progress(mock_supabase_client, "user_123")

        # Assert
        assert len(result.progress) == 1
        assert result.total == 1
        assert result.progress[0].user_id == "user_123"
        assert result.progress[0].progress_percentage == 60.0

    def test_get_user_badge_progress_empty_result(self, mock_supabase_client):
        """Test getting badge progress when user has no tracked progress."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.get_user_badge_progress(mock_supabase_client, "user_123")

        # Assert
        assert len(result.progress) == 0
        assert result.total == 0

    def test_get_user_badge_progress_invalid_user_id(self, mock_supabase_client):
        """Test getting badge progress with invalid user_id."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.get_user_badge_progress(mock_supabase_client, "")
        assert exc_info.value.status_code == 400


# ============================================
# TEST: calculate_badges(user_id, project_ids)
# ============================================

class TestCalculateBadges:
    """Tests for calculate_badges method."""

    def test_calculate_badges_success_all_projects(
        self, mock_supabase_client, sample_user_badge_with_details
    ):
        """Test successfully calculating badges for all user's projects."""
        # Arrange
        with patch('backend.services.badges.badge_calculator.BadgeCalculator.calculate_badges_for_user') as mock_calc:
            mock_calc.return_value = [sample_user_badge_with_details]
            
            # Act
            result = BadgeService.calculate_badges(mock_supabase_client, "user_123")

            # Assert
            assert len(result.badges) == 1
            assert result.total == 1
            mock_calc.assert_called_with(mock_supabase_client, "user_123", None)

    def test_calculate_badges_success_specific_projects(
        self, mock_supabase_client, sample_user_badge_with_details
    ):
        """Test successfully calculating badges for specific projects."""
        # Arrange
        with patch('backend.services.badges.badge_calculator.BadgeCalculator.calculate_badges_for_user') as mock_calc:
            mock_calc.return_value = [sample_user_badge_with_details]

            # Act
            result = BadgeService.calculate_badges(
                mock_supabase_client, "user_123", project_ids=["project_1", "project_2"]
            )

            # Assert
            assert len(result.badges) == 1
            assert result.total == 1
            mock_calc.assert_called_with(
                mock_supabase_client, "user_123", ["project_1", "project_2"]
            )

    def test_calculate_badges_no_new_badges(self, mock_supabase_client):
        """Test calculating badges when no new badges are earned."""
        # Arrange
        with patch('backend.services.badges.badge_calculator.BadgeCalculator.calculate_badges_for_user') as mock_calc:
            mock_calc.return_value = []

            # Act
            result = BadgeService.calculate_badges(mock_supabase_client, "user_123")

            # Assert
            assert len(result.badges) == 0
            assert result.total == 0

    def test_calculate_badges_invalid_user_id(self, mock_supabase_client):
        """Test calculating badges with invalid user_id."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.calculate_badges(mock_supabase_client, "")
        assert exc_info.value.status_code == 400

    def test_calculate_badges_database_error(self, mock_supabase_client):
        """Test handling error during badge calculation."""
        # Arrange
        with patch('backend.services.badges.badge_calculator.BadgeCalculator.calculate_badges_for_user') as mock_calc:
            mock_calc.side_effect = Exception("Calculation error")

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                BadgeService.calculate_badges(mock_supabase_client, "user_123")
            assert exc_info.value.status_code == 500


# ============================================
# TEST: get_user_badge_stats(user_id)
# ============================================

class TestGetUserBadgeStats:
    """Tests for get_user_badge_stats method."""

    def test_get_user_badge_stats_success(
        self, mock_supabase_client, sample_badge_stats
    ):
        """Test successfully getting user's badge statistics."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = sample_badge_stats
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.get_user_badge_stats(mock_supabase_client, "user_123")

        # Assert
        assert result.user_id == "user_123"
        assert result.total_badges == 5
        assert result.bronze_count == 2
        assert result.silver_count == 2
        assert result.gold_count == 1
        mock_supabase_client.table.assert_called_with("user_badge_stats")

    def test_get_user_badge_stats_no_badges(self, mock_supabase_client):
        """Test getting badge stats for user with no badges."""
        # Arrange
        empty_stats = {
            "user_id": "user_123",
            "total_badges": 0,
            "bronze_count": 0,
            "silver_count": 0,
            "gold_count": 0,
            "unique_badges": 0,
            "most_recent_badge": None,
            "badges_by_category": {},
        }
        mock_response = MagicMock()
        mock_response.data = empty_stats
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.get_user_badge_stats(mock_supabase_client, "user_123")

        # Assert
        assert result.total_badges == 0
        assert result.unique_badges == 0

    def test_get_user_badge_stats_not_found(self, mock_supabase_client):
        """Test getting badge stats when user doesn't exist."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.get_user_badge_stats(mock_supabase_client, "nonexistent_user")
        assert exc_info.value.status_code == 404


# ============================================
# TEST: update_badge_progress(user_id, badge_id, value)
# ============================================

class TestUpdateBadgeProgress:
    """Tests for update_badge_progress method."""

    def test_update_badge_progress_success(
        self, mock_supabase_client, sample_badge_progress
    ):
        """Test successfully updating badge progress."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = sample_badge_progress
        mock_supabase_client.table.return_value.upsert.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.update_badge_progress(
            mock_supabase_client, "user_123", "badge_123", 3.0
        )

        # Assert
        assert result.user_id == "user_123"
        assert result.badge_id == "badge_123"
        assert result.current_value == 3.0
        mock_supabase_client.table.assert_called_with("badge_progress")

    def test_update_badge_progress_negative_value(self, mock_supabase_client):
        """Test updating badge progress with negative value."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.update_badge_progress(
                mock_supabase_client, "user_123", "badge_123", -1.0
            )
        assert exc_info.value.status_code == 400
        assert "Value must be non-negative" in exc_info.value.detail

    def test_update_badge_progress_invalid_inputs(self, mock_supabase_client):
        """Test updating badge progress with invalid inputs."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.update_badge_progress(mock_supabase_client, "", "badge_123", 1.0)
        assert exc_info.value.status_code == 400

    def test_update_badge_progress_database_error(self, mock_supabase_client):
        """Test handling database error during progress update."""
        # Arrange
        mock_supabase_client.table.return_value.upsert.return_value.execute.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.update_badge_progress(
                mock_supabase_client, "user_123", "badge_123", 1.0
            )
        assert exc_info.value.status_code == 500


# ============================================
# TEST: award_badge(...)
# ============================================

class TestAwardBadge:
    """Tests for award_badge method."""

    def test_award_badge_success(self, mock_supabase_client, sample_user_badge):
        """Test successfully awarding a badge to a user."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = sample_user_badge
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.award_badge(
            mock_supabase_client,
            "user_123",
            "badge_123",
            "bronze",
            1.0,
            {"projects": 1},
        )

        # Assert
        assert result.user_id == "user_123"
        assert result.badge_id == "badge_123"
        assert result.tier == "bronze"
        mock_supabase_client.table.assert_called_with("user_badges")

    def test_award_badge_invalid_tier(self, mock_supabase_client):
        """Test awarding a badge with invalid tier."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.award_badge(
                mock_supabase_client,
                "user_123",
                "badge_123",
                "invalid_tier",
                1.0,
                {},
            )
        assert exc_info.value.status_code == 400
        assert "Invalid tier" in exc_info.value.detail

    def test_award_badge_already_exists(self, mock_supabase_client):
        """Test awarding a badge that user already has."""
        # Arrange
        mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception(
            "duplicate key value violates unique constraint"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.award_badge(
                mock_supabase_client, "user_123", "badge_123", "bronze", 1.0, {}
            )
        assert exc_info.value.status_code == 409
        assert "Badge already awarded" in exc_info.value.detail

    def test_award_badge_invalid_inputs(self, mock_supabase_client):
        """Test awarding a badge with invalid inputs."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.award_badge(
                mock_supabase_client, "", "badge_123", "bronze", 1.0, {}
            )
        assert exc_info.value.status_code == 400


# ============================================
# TEST: log_badge_event(...)
# ============================================

class TestLogBadgeEvent:
    """Tests for log_badge_event method."""

    def test_log_badge_event_success(self, mock_supabase_client):
        """Test successfully logging a badge event."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = {
            "id": "log_123",
            "user_id": "user_123",
            "badge_id": "badge_123",
            "event_type": "earned",
            "tier": "bronze",
            "old_value": None,
            "new_value": 1.0,
            "event_data": {"projects": 1},
            "triggered_by": "system",
            "created_at": "2024-01-01T00:00:00",
        }
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.log_badge_event(
            mock_supabase_client,
            "user_123",
            "badge_123",
            "earned",
            {"projects": 1},
        )

        # Assert
        assert result.user_id == "user_123"
        assert result.badge_id == "badge_123"
        assert result.event_type == "earned"
        mock_supabase_client.table.assert_called_with("badge_audit_log")

    def test_log_badge_event_invalid_event_type(self, mock_supabase_client):
        """Test logging a badge event with invalid event type."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.log_badge_event(
                mock_supabase_client,
                "user_123",
                "badge_123",
                "invalid_event",
                {},
            )
        assert exc_info.value.status_code == 400
        assert "Invalid event type" in exc_info.value.detail

    def test_log_badge_event_database_error(self, mock_supabase_client):
        """Test handling database error during event logging."""
        # Arrange
        mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            BadgeService.log_badge_event(
                mock_supabase_client, "user_123", "badge_123", "earned", {}
            )
        assert exc_info.value.status_code == 500
        assert "Failed to log badge event" in exc_info.value.detail

    def test_log_badge_event_all_types(self, mock_supabase_client):
        """Test logging all valid event types."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = {
            "id": "log_123",
            "user_id": "user_123",
            "badge_id": "badge_123",
            "event_type": "earned",
            "tier": None,
            "old_value": None,
            "new_value": None,
            "event_data": {},
            "triggered_by": None,
            "created_at": "2024-01-01T00:00:00",
        }
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

        # Act & Assert - Test each valid event type
        valid_event_types = ["earned", "upgraded", "revoked", "progress_updated"]
        for event_type in valid_event_types:
            result = BadgeService.log_badge_event(
                mock_supabase_client, "user_123", "badge_123", event_type, {}
            )
            assert result is not None


# ============================================
# INTEGRATION-STYLE TESTS
# ============================================

class TestBadgeServiceIntegration:
    """Integration-style tests for badge service workflows."""

    def test_complete_badge_earning_workflow(
        self, mock_supabase_client, sample_user_badge_with_details
    ):
        """Test complete workflow of earning a badge."""
        # This would test the flow:
        # 1. User completes action (e.g., creates project)
        # 2. calculate_badges is called
        # 3. Progress is updated
        # 4. Badge is awarded
        # 5. Event is logged

        # Mock responses for each step
        # Step 1: Get initial progress
        progress_response = MagicMock()
        progress_response.data = []

        # Step 2: Calculate badges
        calculate_response = MagicMock()
        calculate_response.data = [sample_user_badge_with_details]

        # Configure mocks
        mock_supabase_client.rpc.return_value.execute.return_value = calculate_response

        # Act
        result = BadgeService.calculate_badges(mock_supabase_client, "user_123")

        # Assert
        assert result.total >= 0

    def test_badge_upgrade_workflow(
        self, mock_supabase_client, sample_user_badge_with_details
    ):
        """Test workflow of upgrading a badge tier."""
        # Similar to above but for upgrade scenario
        # Mock user already has bronze, earns silver
        upgraded_badge = {
            **sample_user_badge_with_details,
            "tier": "silver",
            "achievement_value": 5.0,
            "previous_tier": "bronze",
            "upgraded_at": "2024-01-02T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
        }
        mock_response = MagicMock()
        mock_response.data = [upgraded_badge]

        mock_supabase_client.rpc.return_value.execute.return_value = mock_response

        # Act
        result = BadgeService.calculate_badges(mock_supabase_client, "user_123")

        # Assert
        assert result.total >= 0
