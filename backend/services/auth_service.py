"""
Auth Service - Handle authentication operations with Supabase
"""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from fastapi import HTTPException
from supabase import create_client, Client
import jwt
import httpx
import traceback

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
    async def sign_up(email: str, password: str, captcha_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Sign up a new user
        
        Args:
            email: User's email
            password: User's password
            captcha_token: hCaptcha response token (optional)
            
        Returns:
            Dict containing user and session data
        """
        try:
            supabase = AuthService.get_supabase_client()
            
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
    async def sign_in(email: str, password: str, mfa_challenge_id: Optional[str] = None, mfa_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Sign in an existing user
        
        Args:
            email: User's email
            password: User's password
            mfa_challenge_id: MFA challenge ID if verifying MFA code
            mfa_code: MFA code if verifying MFA challenge
            
        Returns:
            Dict containing user and session data, or MFA challenge info
        """
        try:
            supabase = AuthService.get_supabase_client()
            
            # If MFA challenge ID and code provided, verify MFA
            if mfa_challenge_id and mfa_code:
                response = supabase.auth.mfa.verify({
                    "challenge_id": mfa_challenge_id,
                    "code": mfa_code
                })
                
                if response.user is None or response.session is None:
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid MFA code"
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
                    },
                    "requires_mfa": False
                }
            
            # Initial sign in with password
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Check if MFA is required (user exists but no session)
            if response.user is not None and response.session is None:
                # MFA is required - need to use anon key client with user's access token
                # The response might have an access_token even without a full session
                # Create a new client with anon key for MFA operations
                url = os.getenv("SUPABASE_URL")
                anon_key = os.getenv("SUPABASE_ANON_KEY")
                
                if not url or not anon_key:
                    raise HTTPException(
                        status_code=500,
                        detail="Supabase configuration not found"
                    )
                
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
                                
                                return {
                                    "user": {
                                        "id": response.user.id,
                                        "email": response.user.email,
                                        "created_at": response.user.created_at
                                    },
                                    "session": None,
                                    "requires_mfa": True,
                                    "mfa_challenge_id": challenge_id,
                                    "mfa_factors": [
                                        {
                                            "id": getattr(f, 'id', ''),
                                            "type": getattr(f, 'factor_type', getattr(f, 'type', '')),
                                            "friendly_name": getattr(f, 'friendly_name', None),
                                            "status": getattr(f, 'status', 'verified')
                                        }
                                        for f in factors
                                    ]
                                }
                except Exception as mfa_error:
                    print(f"MFA setup error: {mfa_error}")
                    # If we can't get factors, still return MFA required
                    # The frontend will need to handle this case
                    return {
                        "user": {
                            "id": response.user.id,
                            "email": response.user.email,
                            "created_at": response.user.created_at
                        },
                        "session": None,
                        "requires_mfa": True,
                        "mfa_challenge_id": None,
                        "mfa_factors": []
                    }
            
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
                },
                "requires_mfa": False
            }
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

    @staticmethod
    async def mfa_enroll(access_token: str, friendly_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Enroll user in MFA (TOTP)
        
        Args:
            access_token: User's access token
            friendly_name: Friendly name for the factor
            
        Returns:
            Dict containing factor ID, QR code, and secret
        """
        try:
            # MFA enrollment must be done via user API (not Admin API)
            # Use the user's access token directly
            url = os.getenv("SUPABASE_URL")
            anon_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not anon_key:
                raise HTTPException(
                    status_code=500,
                    detail="Supabase configuration not found"
                )
            
            # Use user API endpoint with user's access token
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{url}/auth/v1/factors",
                    headers={
                        "apikey": anon_key,
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "friendly_name": friendly_name or "Authenticator App",
                        "factor_type": "totp"
                    }
                )
                
                if response.status_code != 200:
                    print(f"User API error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to enroll in MFA: {response.text}"
                    )
                
                data = response.json()
                
                # Debug: print full response
                print(f"DEBUG - MFA enroll response: {data}")
                
                # Handle different response structures
                if isinstance(data, dict):
                    # Supabase returns: { "id": "...", "type": "totp", "totp": { "qr_code": "...", "secret": "..." } }
                    factor_id = data.get("id", "")
                    factor_type = data.get("type", data.get("factor_type", ""))
                    
                    # Get TOTP data - could be nested in "totp" key or at root
                    totp_data = data.get("totp", {})
                    if not totp_data:
                        # Try root level
                        totp_data = data
                    
                    qr_code = totp_data.get("qr_code") or data.get("qr_code")
                    secret = totp_data.get("secret") or data.get("secret")
                    
                    if not qr_code or not secret:
                        print(f"DEBUG - Missing QR code or secret. Full data: {data}")
                        raise HTTPException(
                            status_code=400,
                            detail="MFA enrollment response missing QR code or secret"
                        )
                    
                    return {
                        "id": factor_id,
                        "type": factor_type,
                        "qr_code": qr_code,
                        "secret": secret,
                        "friendly_name": data.get("friendly_name", friendly_name or "Authenticator App")
                    }
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Unexpected response format from MFA enrollment"
                    )
        except HTTPException:
            raise
        except Exception as e:
            print(f"MFA enroll error: {e}")
            traceback.print_exc()
            raise HTTPException(
                status_code=400,
                detail=f"Failed to enroll in MFA: {str(e)}"
            )

    @staticmethod
    async def mfa_verify_enrollment(access_token: str, factor_id: str, code: str) -> Dict[str, Any]:
        """
        Verify MFA enrollment with a code
        
        Args:
            access_token: User's access token
            factor_id: Factor ID to verify
            code: TOTP code from authenticator app
            
        Returns:
            Dict with success status
        """
        try:
            # MFA verification must be done via user API (not Admin API)
            url = os.getenv("SUPABASE_URL")
            anon_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not anon_key:
                raise HTTPException(
                    status_code=500,
                    detail="Supabase configuration not found"
                )
            
            async with httpx.AsyncClient() as client:
                # First create a challenge
                challenge_response = await client.post(
                    f"{url}/auth/v1/factors/{factor_id}/challenge",
                    headers={
                        "apikey": anon_key,
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if challenge_response.status_code != 200:
                    print(f"Challenge error: {challenge_response.status_code} - {challenge_response.text}")
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to create MFA challenge"
                    )
                
                challenge_data = challenge_response.json()
                challenge_id = challenge_data.get("id")
                
                if not challenge_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to create MFA challenge"
                    )
                
                # Then verify the challenge
                verify_response = await client.post(
                    f"{url}/auth/v1/factors/{factor_id}/verify",
                    headers={
                        "apikey": anon_key,
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "challenge_id": challenge_id,
                        "code": code
                    }
                )
                
                if verify_response.status_code != 200:
                    print(f"Verify error: {verify_response.status_code} - {verify_response.text}")
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid verification code"
                    )
            
            return {
                "success": True,
                "message": "MFA enrollment verified successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"MFA verify enrollment error: {e}")
            traceback.print_exc()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid verification code: {str(e)}"
            )

    @staticmethod
    async def mfa_list_factors(access_token: str) -> Dict[str, Any]:
        """
        List all MFA factors for a user
        
        Args:
            access_token: User's access token
            
        Returns:
            Dict containing list of factors
        """
        try:
            # Get user ID from token first
            user_id = await AuthService.verify_token(access_token)
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            # Use Admin API to list factors (requires service role key)
            url = os.getenv("SUPABASE_URL")
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if not url or not service_key:
                raise HTTPException(
                    status_code=500,
                    detail="Supabase configuration not found"
                )
            
            # Use Admin API endpoint
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{url}/auth/v1/admin/users/{user_id}/factors",
                    headers={
                        "apikey": service_key,
                        "Authorization": f"Bearer {service_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 404:
                    # User has no factors
                    return {"factors": []}
                
                if response.status_code != 200:
                    print(f"Admin API error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to list MFA factors"
                    )
                
                data = response.json()
                factors = data if isinstance(data, list) else data.get('factors', [])
                
                return {
                    "factors": [
                        {
                            "id": f.get("id", ""),
                            "type": f.get("factor_type", f.get("type", "")),
                            "friendly_name": f.get("friendly_name"),
                            "status": f.get("status", "verified")
                        }
                        for f in factors
                    ]
                }
        except HTTPException:
            raise
        except Exception as e:
            print(f"MFA list factors error: {e}")
            traceback.print_exc()
            raise HTTPException(
                status_code=400,
                detail=f"Failed to list MFA factors: {str(e)}"
            )

    @staticmethod
    async def mfa_unenroll(access_token: str, factor_id: str) -> Dict[str, Any]:
        """
        Unenroll (remove) an MFA factor
        
        Args:
            access_token: User's access token
            factor_id: Factor ID to remove
            
        Returns:
            Dict with success status
        """
        try:
            # Get user ID from token
            user_id = await AuthService.verify_token(access_token)
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            # Use Admin API to unenroll MFA factor
            url = os.getenv("SUPABASE_URL")
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if not url or not service_key:
                raise HTTPException(
                    status_code=500,
                    detail="Supabase configuration not found"
                )
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{url}/auth/v1/admin/users/{user_id}/factors/{factor_id}",
                    headers={
                        "apikey": service_key,
                        "Authorization": f"Bearer {service_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code not in [200, 204]:
                    print(f"Admin API error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to remove MFA factor"
                    )
            
            return {
                "success": True,
                "message": "MFA factor removed successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"MFA unenroll error: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to remove MFA factor: {str(e)}"
            )

    @staticmethod
    async def mfa_challenge(access_token: str, factor_id: str) -> Dict[str, Any]:
        """
        Create an MFA challenge for sign-in
        
        Args:
            access_token: User's access token (from initial sign-in)
            factor_id: Factor ID to challenge
            
        Returns:
            Dict containing challenge ID
        """
        try:
            supabase = AuthService.get_supabase_client()
            supabase.postgrest.auth(access_token)
            
            challenge_response = supabase.auth.mfa.challenge({"factor_id": factor_id})
            challenge_id = challenge_response.id if hasattr(challenge_response, 'id') else None
            
            if not challenge_id:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to create MFA challenge"
                )
            
            return {
                "challenge_id": challenge_id
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"MFA challenge error: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create MFA challenge: {str(e)}"
            )

