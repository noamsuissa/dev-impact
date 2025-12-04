from typing import Optional, Dict, Any
from fastapi import HTTPException
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """Get Supabase client from environment"""
    url = os.getenv("SUPABASE_URL")
    # Use service role key for backend operations
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration not found"
        )
    
    return create_client(url, key)

async def verify_token(access_token: str) -> Optional[str]:
    """
    Verify access token and return user ID
    
    Args:
        access_token: User's access token
        
    Returns:
        User ID if valid, None otherwise
    """
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(access_token)
        
        if user and user.user:
            return user.user.id
        return None
    except Exception as e:
        print(f"Verify token error: {e}")
        return None

async def get_session(access_token: str) -> Dict[str, Any]:
        """
        Get current session
        
        Args:
            access_token: User's access token
            
        Returns:
            Dict containing user and session data
        """
        try:
            supabase = get_supabase_client()
            # Set the authorization header
            supabase.postgrest.auth(access_token)
            
            # Get user from token
            user = supabase.auth.get_user(access_token)
            
            if user is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            return {
                "user": {
                    "id": user.user.id,
                    "email": user.user.email,
                    "created_at": user.user.created_at
                },
                "session": {
                    "access_token": access_token,
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get session error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

async def refresh_session(refresh_token: str) -> Dict[str, Any]:
        """
        Refresh user session
        
        Args:
            refresh_token: User's refresh token
            
        Returns:
            Dict containing new session data
        """
        try:
            supabase = get_supabase_client()
            response = supabase.auth.refresh_session(refresh_token)
            
            if response.session is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired refresh token"
                )
            
            return {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at
                },
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Refresh session error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired refresh token"
            )