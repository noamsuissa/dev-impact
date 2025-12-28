"""
Shared pytest fixtures and configuration for all tests.

This file contains common fixtures that can be used across all test modules.
"""
import pytest
from unittest.mock import MagicMock


# ============================================
# COMMON FIXTURES
# ============================================

@pytest.fixture
def mock_supabase_client():
    """
    Mock Supabase client for testing.
    
    Returns a MagicMock that can be used to simulate Supabase client behavior.
    Configure return values as needed in individual tests.
    
    Example:
        mock_response = MagicMock()
        mock_response.data = [{"id": "123"}]
        mock_supabase_client.table().select().execute().return_value = mock_response
    """
    return MagicMock()
