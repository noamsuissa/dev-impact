"""
FastAPI dependency injection functions for database clients.
Provides clean, declarative dependency injection for routers.
"""
from typing import Annotated
from fastapi import Depends
from backend.db import client as db_client
from supabase import Client


def get_service_db_client() -> Client:
    """
    FastAPI dependency that provides a service-level Supabase client.
    
    Used for all database operations (read/write) in the service layer.
    This client uses the service role key and bypasses RLS policies.
    
    Returns:
        Supabase client configured with service role credentials
    """
    return db_client.get_service_client()


# Type alias for cleaner router signatures
ServiceDBClient = Annotated[Client, Depends(get_service_db_client)]

