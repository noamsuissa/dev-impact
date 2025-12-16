from supabase import create_client, Client
import os
from fastapi import HTTPException
from typing import Optional

def get_service_client() -> Client:
    try:
        return create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        )
    except Exception as e:
        print(f"Failed to create service client: {e}")
        raise HTTPException(status_code=500, detail="Failed to create service client")

def get_user_client(access_token: Optional[str] = None) -> Client:
    try:
        client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_ANON_KEY"],
        )
        if access_token:
            client.postgrest.auth(access_token)
        return client
    except Exception as e:
        print(f"Failed to create user client: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user client")
