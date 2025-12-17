"""
Auth Service - Handle authentication operations with Supabase
"""
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import HTTPException
import jwt
import httpx
import traceback
from supabase import Client
from backend.db.client import get_user_client, get_service_client
from gotrue.types import SignUpWithEmailAndPasswordCredentials, SignUpWithEmailAndPasswordCredentialsOptions
from backend.schemas.auth import (
    AuthResponse,
    UserResponse,
    SessionResponse,
    MessageResponse,
    MFAFactorResponse
)

# Load environment variables
load_dotenv()


class AuthService:
    """Service for handling authentication operations with Supabase."""    

    @staticmethod
    async def sign_up(email: str, password: str, captcha_token: Optional[str] = None) -> AuthResponse:
        """
        Sign up a new user
        
        Args:
            email: User's email
            password: User's password
            captcha_token: hCaptcha response token (optional)
            
        Returns:
            AuthResponse containing user and session data
        """
        try:
            supabase = get_service_client()
            
            # Get redirect URL from environment (fallback to localhost for dev)
            redirect_url = os.getenv("AUTH_REDIRECT_URL", "http://localhost:5173")
            
            options = SignUpWithEmailAndPasswordCredentialsOptions(
                email_redirect_to=redirect_url
            )
            
            # Add captcha token only if provided and not localhost bypass
            if captcha_token and captcha_token != 'localhost_bypass':
                options["captcha_token"] = captcha_token
            
            response = supabase.auth.sign_up(SignUpWithEmailAndPasswordCredentials(
                email=email,
                password=password,
                options=options
            ))
            
            if response.user is None:
                raise HTTPException(status_code=400, detail="Failed to create account. Email may already be registered.")
            
            return AuthResponse(
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    created_at=response.user.created_at
                ),
                session=SessionResponse(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token if response.session else None,
                    expires_at=response.session.expires_at if response.session else None,
                ) if response.session else None,
                requires_email_verification=response.session is None
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Sign up error: {e}")
            raise HTTPException(status_code=400, detail=f"Sign up error: {e}")

    @staticmethod
    async def sign_in(
        email: str, 
        password: str, 
        mfa_challenge_id: Optional[str] = None, 
        mfa_code: Optional[str] = None, 
        mfa_factor_id: Optional[str] = None
    ) -> AuthResponse:
        """Sign in user with email/password and optional MFA verification"""
        try:
            supabase = get_service_client()
            
            # Handle MFA verification flow
            if mfa_challenge_id and mfa_code:
                if not mfa_factor_id:
                    raise HTTPException(status_code=400, detail="Factor ID is required for MFA verification")
                
                return await AuthService._verify_mfa_and_signin(
                    email, password, mfa_challenge_id, mfa_code, mfa_factor_id, supabase
                )
            
            # Initial password sign-in
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not response.user:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            # Check if MFA is required
            if response.user and not response.session:
                # User has MFA enabled - get factors and create challenge
                factors_response = supabase.auth.mfa.list_factors()
                factors = factors_response.totp if hasattr(factors_response, 'totp') else []
                
                if factors:
                    factor = factors[0]
                    challenge_response = supabase.auth.mfa.challenge({"factor_id": factor.id})
                    
                    return AuthResponse(
                        user=UserResponse(
                            id=response.user.id,
                            email=response.user.email,
                            created_at=response.user.created_at
                        ),
                        session=None,
                        requires_mfa=True,
                        mfa_challenge_id=challenge_response.id,
                        mfa_factor_id=factor.id,
                        mfa_factors=[
                            MFAFactorResponse(
                                id=f.id,
                                type=f.factor_type,
                                friendly_name=f.friendly_name,
                                status=f.status
                            )
                            for f in factors
                        ]
                    )
            
            if not response.session:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
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
                requires_mfa=False
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Sign in error: {e}")
            traceback.print_exc()
            error_str = str(e).lower()
            if "mfa" in error_str or "challenge" in error_str:
                raise HTTPException(status_code=401, detail="Invalid MFA code")
            raise HTTPException(status_code=401, detail="Invalid email or password")


    @staticmethod
    async def _verify_mfa_and_signin(
        email: str, 
        password: str, 
        challenge_id: str, 
        code: str, 
        factor_id: str,
        supabase: Client
    ) -> AuthResponse:
        """Verify MFA code and complete sign-in"""
    
        # Sign in with password first
        password_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if not password_response.user or not password_response.session:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        try:
            # Verify MFA using Supabase's built-in method
            supabase.auth.mfa.verify({
                "factor_id": factor_id,
                "challenge_id": challenge_id,
                "code": code
            })
            
            # If verify() doesn't raise an exception, the code was valid
            # Refresh the session to get AAL2 tokens
            session_response = supabase.auth.refresh_session(password_response.session.refresh_token)
            
            if not session_response.user or not session_response.session:
                raise HTTPException(status_code=401, detail="Failed to complete MFA verification")
            
            return AuthResponse(
                user=UserResponse(
                    id=session_response.user.id,
                    email=session_response.user.email,
                    created_at=session_response.user.created_at
                ),
                session=SessionResponse(
                    access_token=session_response.session.access_token,
                    refresh_token=session_response.session.refresh_token,
                    expires_at=session_response.session.expires_at,
                ),
                requires_mfa=False
            )
        except Exception as e:
            print(f"MFA verify error: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Invalid MFA code")

    @staticmethod
    async def sign_out(access_token: str) -> MessageResponse:
        """
        Sign out a user
        
        Args:
            access_token: User's access token
            
        Returns:
            MessageResponse with success status
        """
        try:
            supabase = get_user_client(access_token)
            # Set the user's session
            supabase.auth.sign_out()
            
            return MessageResponse(success=True, message="Signed out successfully")
        except Exception as e:
            print(f"Sign out error: {e}")
            # Even if sign out fails, we still return success as the client will clear local tokens
            return MessageResponse(success=True, message="Signed out")

    @staticmethod
    async def reset_password_email(email: str) -> MessageResponse:
        """
        Send password reset email
        
        Args:
            email: User's email
            
        Returns:
            MessageResponse with success status
        """
        try:
            supabase = get_service_client()
            
            # Get redirect URL from environment (fallback to localhost for dev)
            redirect_url = os.getenv("AUTH_REDIRECT_URL", "http://localhost:5173")
            
            supabase.auth.reset_password_email(
                email,
                options={
                    "redirect_to": redirect_url
                }
            )
            
            return MessageResponse(success=True, message="Password reset email sent")
        except Exception as e:
            print(f"Reset password email error: {e}")
            # Return success even on error to prevent email enumeration
            return MessageResponse(success=True, message="If an account exists, a password reset email has been sent")

    @staticmethod
    async def update_password(access_token: str, new_password: str) -> MessageResponse:
        """
        Update user password
        
        Args:
            access_token: User's access token from recovery link
            new_password: New password
            
        Returns:
            MessageResponse with success status
        """
        try:
            # Create client and set the session
            supabase = get_service_client()
            supabase.auth.set_session(access_token, refresh_token="")  # Recovery tokens don't have refresh tokens
            
            # Update password using the authenticated client
            supabase.auth.update_user({"password": new_password})
            
            return MessageResponse(success=True, message="Password updated successfully")
            
        except Exception as e:
            print(f"Update password error: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=400, detail="Failed to update password")

    