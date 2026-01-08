"""
Database client factory for Supabase connections.
Centralizes client creation logic for dependency injection.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def get_service_client() -> Client:
    """
    Get Supabase client with service role key for backend operations.

    This client has elevated permissions and should be used for:
    - INSERT, UPDATE, DELETE, UPSERT operations
    - Operations that bypass RLS policies
    - Server-side business logic

    Returns:
        Configured Supabase client with service role key

    Raises:
        RuntimeError: If Supabase configuration is missing
    """
    url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not service_role_key:
        raise RuntimeError(
            "Supabase configuration not found. "
            "Ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set."
        )

    return create_client(url, service_role_key)
