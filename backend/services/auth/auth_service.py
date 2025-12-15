"""
Auth Service - Handle authentication operations with Supabase
"""
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import HTTPException
from supabase import create_client
import jwt
import httpx
import traceback
from ...utils import auth_utils
from ...schemas.auth import (
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
            supabase = auth_utils.get_supabase_client()
            
            # Get redirect URL from environment (fallback to localhost for dev)
            redirect_url = os.getenv("AUTH_REDIRECT_URL", "http://localhost:5173")
            
            options = {
                "email_redirect_to": redirect_url
            }
            
            # Add captcha token only if provided and not localhost bypass
            if captcha_token and captcha_token != 'localhost_bypass':
                options["captcha_token"] = captcha_token
            
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": options
            })
            
            if response.user is None:
                raise HTTPException(status_code=400, detail="Failed to create account. Email may already be registered.")
            
            return AuthResponse(
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    created_at=response.user.created_at
                ),
                session=SessionResponse(
                    access_token=response.session.access_token if response.session else None,
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
    async def sign_in(email: str, password: str, mfa_challenge_id: Optional[str] = None, mfa_code: Optional[str] = None, mfa_factor_id: Optional[str] = None) -> AuthResponse:
        """
        Sign in an existing user
        
        Args:
            email: User's email
            password: User's password
            mfa_challenge_id: MFA challenge ID if verifying MFA code
            mfa_code: MFA code if verifying MFA challenge
            mfa_factor_id: MFA factor ID if verifying MFA challenge
            
        Returns:
            AuthResponse containing user and session data, or MFA challenge info
        """
        try:
            supabase = auth_utils.get_supabase_client()
            
            # If MFA challenge ID and code provided, verify MFA
            if mfa_challenge_id and mfa_code:
                if not mfa_factor_id:
                    raise HTTPException(status_code=400, detail="Factor ID is required for MFA verification")
                
                # First sign in with password to get a session token
                password_response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                if password_response.user is None or password_response.session is None:
                    raise HTTPException(status_code=401, detail="Invalid email or password")
                
                # Use user API endpoint directly to verify MFA challenge
                url = os.getenv("SUPABASE_URL")
                anon_key = os.getenv("SUPABASE_ANON_KEY")
                
                if not url or not anon_key:
                    raise HTTPException(status_code=500, detail="Supabase configuration not found")
                
                try:
                    # Verify using the user API endpoint with factor_id
                    async with httpx.AsyncClient() as client:
                        verify_response = await client.post(
                            f"{url}/auth/v1/factors/{mfa_factor_id}/verify",
                            headers={
                                "apikey": anon_key,
                                "Authorization": f"Bearer {password_response.session.access_token}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "challenge_id": mfa_challenge_id,
                                "code": mfa_code
                            }
                        )
                        
                        if verify_response.status_code != 200:
                            error_text = verify_response.text
                            print(f"MFA verify API error: {verify_response.status_code} - {error_text}")
                            raise HTTPException(status_code=401, detail="Invalid MFA code")
                        
                        # After successful verification, refresh the session to get AAL2 tokens
                        session_response = supabase.auth.refresh_session(password_response.session.refresh_token)
                        
                        if session_response.user is None or session_response.session is None:
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
                except HTTPException:
                    raise
                except Exception as verify_err:
                    print(f"MFA verify error: {verify_err}")
                    traceback.print_exc()
                    raise HTTPException(status_code=401, detail="Invalid MFA code")
            
            # Initial sign in with password
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Check if user has MFA factors enrolled
            # If they do, we need to challenge them even if a session was returned
            user_id = response.user.id if response.user else None
            
            if user_id:
                # Check if user has MFA factors using Admin API
                url = os.getenv("SUPABASE_URL")
                service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
                
                if url and service_key:
                    try:
                        async with httpx.AsyncClient() as client:
                            factors_response = await client.get(
                                f"{url}/auth/v1/admin/users/{user_id}/factors",
                                headers={
                                    "apikey": service_key,
                                    "Authorization": f"Bearer {service_key}",
                                    "Content-Type": "application/json"
                                }
                            )
                            
                            if factors_response.status_code == 200:
                                factors_data = factors_response.json()
                                factors = factors_data if isinstance(factors_data, list) else factors_data.get('factors', [])
                                
                                # Filter for verified TOTP factors
                                verified_totp_factors = [
                                    f for f in factors 
                                    if f.get('factor_type') == 'totp' and f.get('status') == 'verified'
                                ]
                                
                                if verified_totp_factors:
                                    # User has MFA - create challenge using user API with session token
                                    factor_id = verified_totp_factors[0].get('id')
                                    if factor_id:
                                        # Use user API to create challenge (requires user's access token from password sign-in)
                                        anon_key = os.getenv("SUPABASE_ANON_KEY")
                                        if anon_key and response.session and response.session.access_token:
                                            try:
                                                # Use user API endpoint with the session token from password sign-in
                                                async with httpx.AsyncClient() as user_client:
                                                    challenge_response = await user_client.post(
                                                        f"{url}/auth/v1/factors/{factor_id}/challenge",
                                                        headers={
                                                            "apikey": anon_key,
                                                            "Authorization": f"Bearer {response.session.access_token}",
                                                            "Content-Type": "application/json"
                                                        }
                                                    )
                                                    
                                                    if challenge_response.status_code == 200:
                                                        challenge_data = challenge_response.json()
                                                        challenge_id = challenge_data.get("id")
                                                        
                                                        if challenge_id:
                                                            return AuthResponse(
                                                                user=UserResponse(
                                                                    id=response.user.id,
                                                                    email=response.user.email,
                                                                    created_at=response.user.created_at
                                                                ),
                                                                session=None,  # Don't return session until MFA verified
                                                                requires_mfa=True,
                                                                mfa_challenge_id=challenge_id,
                                                                mfa_factor_id=factor_id,  # Include factor_id for verification
                                                                mfa_factors=[
                                                                    MFAFactorResponse(
                                                                        id=f.get("id", ""),
                                                                        type=f.get("factor_type", f.get("type", "")),
                                                                        friendly_name=f.get("friendly_name"),
                                                                        status=f.get("status", "verified")
                                                                    )
                                                                    for f in verified_totp_factors
                                                                ]
                                                            )
                                                    else:
                                                        print(f"User API challenge error: {challenge_response.status_code} - {challenge_response.text}")
                                            except Exception as challenge_err:
                                                print(f"Failed to create MFA challenge: {challenge_err}")
                                                traceback.print_exc()
                                        else:
                                            print("Missing anon key or session token for MFA challenge")
                    except Exception as mfa_check_err:
                        print(f"Error checking MFA factors: {mfa_check_err}")
            
            # Check if MFA is required (user exists but no session) - fallback check
            if response.user is not None and response.session is None:
                # MFA is required - need to use anon key client with user's access token
                # The response might have an access_token even without a full session
                # Create a new client with anon key for MFA operations
                url = os.getenv("SUPABASE_URL")
                anon_key = os.getenv("SUPABASE_ANON_KEY")
                
                if not url or not anon_key:
                    raise HTTPException(status_code=500, detail="Supabase configuration not found")
                
                # Create client with anon key and set auth header if we have a token
                mfa_client = create_client(url, anon_key)
                
                # Try to get access token from response (might be in different location)
                # If not available, we'll need to use the user ID to create challenge
                # For now, try to list factors - this might fail if we need auth
                try:
                    # Set auth header if there's an access_token in response
                    if hasattr(response, 'access_token') and response.access_token:
                        mfa_client.postgrest.auth(response.access_token)
                    
                    factors_response = mfa_client.auth.mfa.list_factors()
                    factors = factors_response.factors if hasattr(factors_response, 'factors') else []
                    
                    if factors and len(factors) > 0:
                        # Create challenge for first TOTP factor
                        totp_factor = next((f for f in factors if getattr(f, 'factor_type', getattr(f, 'type', None)) == 'totp'), None)
                        if totp_factor:
                            factor_id = getattr(totp_factor, 'id', None)
                            if factor_id:
                                challenge_response = mfa_client.auth.mfa.challenge({"factor_id": factor_id})
                                challenge_id = getattr(challenge_response, 'id', None)
                                
                                return AuthResponse(
                                    user=UserResponse(
                                        id=response.user.id,
                                        email=response.user.email,
                                        created_at=response.user.created_at
                                    ),
                                    session=None,
                                    requires_mfa=True,
                                    mfa_challenge_id=challenge_id,
                                    mfa_factors=[
                                        MFAFactorResponse(
                                            id=getattr(f, 'id', ''),
                                            type=getattr(f, 'factor_type', getattr(f, 'type', '')),
                                            friendly_name=getattr(f, 'friendly_name', None),
                                            status=getattr(f, 'status', 'verified')
                                        )
                                        for f in factors
                                    ]
                                )
                except Exception as mfa_error:
                    print(f"MFA setup error: {mfa_error}")
                    # If we can't get factors, still return MFA required
                    # The frontend will need to handle this case
                    return AuthResponse(
                        user=UserResponse(
                            id=response.user.id,
                            email=response.user.email,
                            created_at=response.user.created_at
                        ),
                        session=None,
                        requires_mfa=True,
                        mfa_challenge_id=None,
                        mfa_factors=[]
                    )
            
            if response.user is None or response.session is None:
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
            error_str = str(e).lower()
            if "mfa" in error_str or "challenge" in error_str:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid MFA code"
                )
            raise HTTPException(status_code=401, detail="Invalid email or password")

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
            supabase = auth_utils.get_supabase_client()
            # Set the user's session
            supabase.postgrest.auth(access_token)
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
            supabase = auth_utils.get_supabase_client()
            
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
            # Decode the JWT to get the user ID
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            user_id = decoded.get('sub')
            
            if not user_id:
                raise HTTPException(status_code=400, detail="Invalid token")
            
            # Use service role key to update password directly
            url = os.getenv("SUPABASE_URL")
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if not url or not service_key:
                raise HTTPException(status_code=500, detail="Server configuration error")
            
            # Update password using Admin API
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
                    raise HTTPException(status_code=400, detail="Failed to update password")
            
            return MessageResponse(success=True, message="Password updated successfully")
        except Exception as e:
            print(f"Update password error: {e}")
            raise HTTPException(status_code=400, detail="Failed to update password")

    