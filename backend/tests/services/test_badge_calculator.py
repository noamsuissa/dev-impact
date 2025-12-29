
import pytest
from unittest.mock import MagicMock, patch
from backend.services.badges.badge_calculator import BadgeCalculator
from backend.schemas.badge import (
    BadgeDefinition,
    UserBadgeWithDetails
)

class TestBadgeCalculator:
    """Tests for BadgeCalculator class with LLM integration and batching."""

    @pytest.fixture
    def mock_badges(self):
        """Sample badge definitions."""
        return [
            BadgeDefinition(
                id="badge_1",
                badge_key="speed_demon",
                name="Speed Demon",
                description="Fast API",
                category="performance",
                calculation_type="single_project",
                metric_type="performance",
                bronze_threshold={"min_speed": 100},
                silver_threshold={"min_speed": 200},
                gold_threshold={"min_speed": 300},
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z"
            ),
             BadgeDefinition(
                id="badge_2",
                badge_key="secure_api",
                name="Secure API",
                description="Secure API",
                category="security",
                calculation_type="single_project",
                metric_type="security",
                bronze_threshold={"score": 80},
                silver_threshold={"score": 90},
                gold_threshold={"score": 95},
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z"
            )
        ]

    @patch("backend.services.badges.badge_calculator.LiteLLMProvider")
    def test_calculate_badges_pro_gold_multiple(self, mock_llm_cls, mock_supabase_client, mock_badges):
        """Test Pro user earning data for multiple badges via batch LLM call."""
        # Arrange
        # Mock LLM instance
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm
        
        # Mock LLM response: Batch result
        mock_llm.generate_completion_sync.return_value = {
            "content": """
            {
                "earned_badges": [
                    {"key": "speed_demon", "tier": "gold", "reason": "Fast enough"},
                    {"key": "secure_api", "tier": "silver", "reason": "Good security"}
                ]
            }
            """
        }

        # Mock Supabase responses
        mock_badges_query = MagicMock()
        mock_badges_query.execute.return_value.data = [b.model_dump() for b in mock_badges]
        
        # Metrics for ONE project that covers both badge types
        metrics_data = [
            {
                "project_id": "proj_1",
                "metric_type": "performance",
                "metric_data": {"speed": 350},
                "project": {"user_id": "user_123", "id": "proj_1"}
            },
            {
                "project_id": "proj_1",
                "metric_type": "security",
                "metric_data": {"score": 92},
                "project": {"user_id": "user_123", "id": "proj_1"}
            }
        ]
        
        mock_metrics_query = MagicMock()
        mock_metrics_query.execute.return_value.data = metrics_data
        
        # Subscription (Pro)
        mock_profile_query = MagicMock()
        mock_profile_query.execute.return_value.data = {"subscription_type": "pro"}

        def table_side_effect(name):
            if name == "badge_definitions":
                m = MagicMock()
                m.select.return_value.eq.return_value = mock_badges_query
                return m
            elif name == "project_metrics":
                m = MagicMock()
                m.select.return_value.eq.return_value = mock_metrics_query
                mock_metrics_query.in_.return_value = mock_metrics_query
                return m
            elif name == "profiles":
                m = MagicMock()
                m.select.return_value.eq.return_value.single.return_value = mock_profile_query
                return m
            return MagicMock()
            
        mock_supabase_client.table.side_effect = table_side_effect

        # Act
        results = BadgeCalculator.calculate_badges_for_user(mock_supabase_client, "user_123")

        # Assert
        assert len(results) == 2
        
        # Verify first badge
        b1 = next(b for b in results if b.badge_key == "speed_demon")
        assert b1.tier == "gold"
        assert b1.achievement_data.get("llm_reason") == "Fast enough" # type: ignore
        
        # Verify second badge
        b2 = next(b for b in results if b.badge_key == "secure_api")
        assert b2.tier == "silver"
        assert b2.achievement_data.get("llm_reason") == "Good security" # type: ignore


    @patch("backend.services.badges.badge_calculator.LiteLLMProvider")
    def test_calculate_badges_free_capped_batch(self, mock_llm_cls, mock_supabase_client, mock_badges):
        """Test Free user capped at Bronze in batch result."""
        # Arrange
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm
        
        # LLM says Gold
        mock_llm.generate_completion_sync.return_value = {
            "content": """
            {
                "earned_badges": [
                    {"key": "speed_demon", "tier": "gold", "reason": "Super fast"}
                ]
            }
            """
        }

        mock_badges_query = MagicMock()
        mock_badges_query.execute.return_value.data = [mock_badges[0].model_dump()]
        
        metrics_data = [{
            "project_id": "proj_1", "metric_type": "performance", "metric_data": {"speed": 350}, "project": {"user_id": "user_123"}
        }]
        mock_metrics_query = MagicMock()
        mock_metrics_query.execute.return_value.data = metrics_data
        
        # Free subscription
        mock_profile_query = MagicMock()
        mock_profile_query.execute.return_value.data = {"subscription_type": "free"}

        def table_side_effect(name):
            if name == "badge_definitions":
                m = MagicMock()
                m.select.return_value.eq.return_value = mock_badges_query
                return m
            elif name == "project_metrics":
                m = MagicMock()
                m.select.return_value.eq.return_value = mock_metrics_query
                return m
            elif name == "profiles":
                m = MagicMock()
                m.select.return_value.eq.return_value.single.return_value = mock_profile_query
                return m
            return MagicMock()
            
        mock_supabase_client.table.side_effect = table_side_effect

        # Act
        results = BadgeCalculator.calculate_badges_for_user(mock_supabase_client, "user_123")

        # Assert
        assert len(results) == 1
        badge = results[0]
        assert badge.badge_key == "speed_demon"
        assert badge.tier == "bronze"  # Capped!
        assert badge.achievement_data.get("eligible_tier") == "gold" # type: ignore # Notification
        assert badge.achievement_data.get("llm_reason") == "Super fast" # type: ignore

    @patch("backend.services.badges.badge_calculator.LiteLLMProvider")
    def test_calculate_badges_llm_rejection(self, mock_llm_cls, mock_supabase_client, mock_badges):
        """Test LLM rejecting a badge."""
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm
        mock_llm.generate_completion_sync.return_value = {
            "content": '{"earned_badges": []}'
        }

        mock_badges_query = MagicMock()
        mock_badges_query.execute.return_value.data = [mock_badges[0].model_dump()]
        
        metrics_data = [{"metric_type": "performance", "metric_data": {"speed": 50}, "project": {"user_id": "user_123"}}]
        mock_metrics_query = MagicMock()
        mock_metrics_query.execute.return_value.data = metrics_data
        
        mock_profile_query = MagicMock()
        mock_profile_query.execute.return_value.data = {"subscription_type": "pro"}

        def table_side_effect(name):
            if name == "badge_definitions":
                m = MagicMock()
                m.select.return_value.eq.return_value = mock_badges_query
                return m
            elif name == "project_metrics":
                m = MagicMock()
                m.select.return_value.eq.return_value = mock_metrics_query
                return m
            elif name == "profiles":
                m = MagicMock()
                m.select.return_value.eq.return_value.single.return_value = mock_profile_query
                return m
            return MagicMock()

        mock_supabase_client.table.side_effect = table_side_effect

        results = BadgeCalculator.calculate_badges_for_user(mock_supabase_client, "user_123")
        assert len(results) == 0
