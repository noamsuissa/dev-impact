from typing import Optional
import jwt
from fastapi import HTTPException, Header
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from ..schemas.auth import AuthResponse, UserResponse, SessionResponse

load_dotenv()

def get_access_token(
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Dependency to extract and validate Bearer token from Authorization header.
    
    Raises HTTPException if token is missing or invalid.
    Returns the access token string.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    return authorization.replace("Bearer ", "")

def get_supabase_client(access_token: Optional[str] = None) -> Client:
    """Get Supabase client from environment"""
    url = os.getenv("SUPABASE_URL")
    # Use service role key for backend operations
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration not found"
        )
    
    client = create_client(url, key)
    
    if access_token and not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        client.postgrest.auth(access_token)
        
    return client

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

async def get_session(access_token: str) -> AuthResponse:
        """
        Get current session
        
        Args:
            access_token: User's access token
            
        Returns:
            AuthResponse containing user and session data
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
            
            return AuthResponse(
                user=UserResponse(
                    id=user.user.id,
                    email=user.user.email,
                    created_at=user.user.created_at
                ),
                session=SessionResponse(
                    access_token=access_token,
                ),
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Get session error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

async def refresh_session(refresh_token: str) -> AuthResponse:
        """
        Refresh user session
        
        Args:
            refresh_token: User's refresh token
            
        Returns:
            AuthResponse containing new session data
        """
        try:
            supabase = get_supabase_client()
            response = supabase.auth.refresh_session(refresh_token)
            
            if response.session is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired refresh token"
                )
            
            return AuthResponse(
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    created_at=response.user.created_at
                ),
                session=SessionResponse(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token,
                    expires_at=response.session.expires_at,
                ),
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Refresh session error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired refresh token"
            )

def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from JWT token"""
    try:
        # Decode JWT without verification (we trust Supabase tokens)
        # In production, you should verify the signature with your Supabase JWT secret
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get('sub')
        return user_id
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def get_user_id_from_authorization(authorization: Optional[str]) -> str:
    """Extract and validate user ID from authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    # Support both "Bearer <token>" and raw token strings
    token = authorization
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")

    user_id = get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    return user_id

def get_user_email_from_authorization(authorization: Optional[str]) -> str:
    """Extract and validate user email from authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    # Support both "Bearer <token>" and raw token strings
    token = authorization
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")
    
    try:
        # Decode JWT without verification (we trust Supabase tokens)
        decoded = jwt.decode(token, options={"verify_signature": False})
        email = decoded.get('email')
        
        if not email:
            raise HTTPException(
                status_code=401,
                detail="Email not found in token"
            )
        
        return email
    except jwt.DecodeError as e:
        print(f"Error decoding token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )