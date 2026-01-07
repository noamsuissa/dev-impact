"""
FastAPI dependency injection functions for database clients.
Provides clean, declarative dependency injection for routers.
"""
from typing import Annotated, Type
from fastapi import Depends
from backend.db import client as db_client
from backend.services.stripe_service import StripeService
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


def get_stripe_service() -> StripeService:
    """
    FastAPI dependency that provides the StripeService class.
    
    Returns:
        StripeService class (used for static method calls)
    """
    return StripeService


# Type aliases for cleaner router signatures
ServiceDBClient = Annotated[Client, Depends(get_service_db_client)]
StripeServiceDep = Annotated[StripeService, Depends(get_stripe_service)]

