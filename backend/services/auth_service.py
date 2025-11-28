"""
Auth Service - Handle authentication operations with Supabase
"""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from fastapi import HTTPException
from supabase import create_client, Client
import jwt

# Load environment variables
load_dotenv()


class AuthService:
    """Service for handling authentication operations with Supabase."""

    @staticmethod
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

    @staticmethod
    async def sign_up(email: str, password: str) -> Dict[str, Any]:
        """
        Sign up a new user
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dict containing user and session data
        """
        try:
            supabase = AuthService.get_supabase_client()
            
            # Get redirect URL from environment (fallback to localhost for dev)
            redirect_url = os.getenv("AUTH_REDIRECT_URL", "http://localhost:5173")
            
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "email_redirect_to": redirect_url
                }
            })
            
            if response.user is None:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to create account. Email may already be registered."
                )
            
            return {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at
                },
                "session": {
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None,
                    "expires_at": response.session.expires_at if response.session else None,
                } if response.session else None,
                "requires_email_verification": response.session is None
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Sign up error: {e}")
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    async def sign_in(email: str, password: str) -> Dict[str, Any]:
        """
        Sign in an existing user
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dict containing user and session data
        """
        try:
            supabase = AuthService.get_supabase_client()
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user is None or response.session is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
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
            print(f"Sign in error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

    @staticmethod
    async def sign_out(access_token: str) -> Dict[str, Any]:
        """
        Sign out a user
        
        Args:
            access_token: User's access token
            
        Returns:
            Dict with success status
        """
        try:
            supabase = AuthService.get_supabase_client()
            # Set the user's session
            supabase.postgrest.auth(access_token)
            supabase.auth.sign_out()
            
            return {"success": True, "message": "Signed out successfully"}
        except Exception as e:
            print(f"Sign out error: {e}")
            # Even if sign out fails, we still return success as the client will clear local tokens
            return {"success": True, "message": "Signed out"}

    @staticmethod
    async def get_session(access_token: str) -> Dict[str, Any]:
        """
        Get current session
        
        Args:
            access_token: User's access token
            
        Returns:
            Dict containing user and session data
        """
        try:
            supabase = AuthService.get_supabase_client()
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

    @staticmethod
    async def refresh_session(refresh_token: str) -> Dict[str, Any]:
        """
        Refresh user session
        
        Args:
            refresh_token: User's refresh token
            
        Returns:
            Dict containing new session data
        """
        try:
            supabase = AuthService.get_supabase_client()
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

    @staticmethod
    async def reset_password_email(email: str) -> Dict[str, Any]:
        """
        Send password reset email
        
        Args:
            email: User's email
            
        Returns:
            Dict with success status
        """
        try:
            supabase = AuthService.get_supabase_client()
            
            # Get redirect URL from environment (fallback to localhost for dev)
            redirect_url = os.getenv("AUTH_REDIRECT_URL", "http://localhost:5173")
            
            supabase.auth.reset_password_email(
                email,
                options={
                    "redirect_to": redirect_url
                }
            )
            
            return {
                "success": True,
                "message": "Password reset email sent"
            }
        except Exception as e:
            print(f"Reset password email error: {e}")
            # Return success even on error to prevent email enumeration
            return {
                "success": True,
                "message": "If an account exists, a password reset email has been sent"
            }

    @staticmethod
    async def update_password(access_token: str, new_password: str) -> Dict[str, Any]:
        """
        Update user password
        
        Args:
            access_token: User's access token from recovery link
            new_password: New password
            
        Returns:
            Dict with success status
        """
        try:
            # Decode the JWT to get the user ID
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            user_id = decoded.get('sub')
            
            if not user_id:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid token"
                )
            
            # Use service role key to update password directly
            url = os.getenv("SUPABASE_URL")
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if not url or not service_key:
                raise HTTPException(
                    status_code=500,
                    detail="Server configuration error"
                )
            
            # Update password using Admin API
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{url}/auth/v1/admin/users/{user_id}",
                    headers={
                        "apikey": service_key,
                        "Authorization": f"Bearer {service_key}",
                        "Content-Type": "application/json"
                    },
                    json={"password": new_password}
                )
                
                if response.status_code not in [200, 204]:
                    print(f"Supabase update password failed: {response.text}")
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to update password"
                    )
            
            return {
                "success": True,
                "message": "Password updated successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Update password error: {e}")
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    async def verify_token(access_token: str) -> Optional[str]:
        """
        Verify access token and return user ID
        
        Args:
            access_token: User's access token
            
        Returns:
            User ID if valid, None otherwise
        """
        try:
            supabase = AuthService.get_supabase_client()
            user = supabase.auth.get_user(access_token)
            
            if user and user.user:
                return user.user.id
            return None
        except Exception as e:
            print(f"Verify token error: {e}")
            return None

