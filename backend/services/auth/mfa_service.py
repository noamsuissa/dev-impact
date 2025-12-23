import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from fastapi import HTTPException
import httpx
import traceback
from backend.utils import auth_utils
from backend.schemas.auth import (
    MessageResponse,
    MFAEnrollResponse,
    MFAListResponse,
    MFAFactorResponse
)

load_dotenv()

class MFAService:
    """Service for handling MFA operations"""

    @staticmethod
    async def mfa_enroll(access_token: str, friendly_name: Optional[str] = None) -> MFAEnrollResponse:
        """
        Enroll user in MFA (TOTP)
        
        Args:
            access_token: User's access token
            friendly_name: Friendly name for the factor
            
        Returns:
            MFAEnrollResponse containing factor ID, QR code, and secret
        """
        try:
            # MFA enrollment must be done via user API (not Admin API)
            # Use the user's access token directly
            url = os.getenv("SUPABASE_URL")
            anon_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not anon_key:
                raise HTTPException(status_code=500, detail="Supabase configuration not found")
            
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
                    raise HTTPException(status_code=400, detail=f"Failed to enroll in MFA: {response.text}")
                
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
                        raise HTTPException(status_code=400, detail="MFA enrollment response missing QR code or secret")
                    
                    return MFAEnrollResponse(
                        id=factor_id,
                        type=factor_type,
                        qr_code=qr_code,
                        secret=secret,
                        friendly_name=data.get("friendly_name", friendly_name or "Authenticator App")
                    )
                else:
                    raise HTTPException(status_code=400, detail="Unexpected response format from MFA enrollment")
        except HTTPException:
            raise
        except Exception as e:
            print(f"MFA enroll error: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"Failed to enroll in MFA")

    @staticmethod
    async def mfa_verify_enrollment(access_token: str, factor_id: str, code: str) -> MessageResponse:
        """
        Verify MFA enrollment with a code
        
        Args:
            access_token: User's access token
            factor_id: Factor ID to verify
            code: TOTP code from authenticator app
            
        Returns:
            MessageResponse with success status
        """
        try:
            # MFA verification must be done via user API (not Admin API)
            url = os.getenv("SUPABASE_URL")
            anon_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not anon_key:
                raise HTTPException(status_code=500, detail="Supabase configuration not found")
            
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
                    raise HTTPException(status_code=400, detail="Failed to create MFA challenge")
                
                challenge_data = challenge_response.json()
                challenge_id = challenge_data.get("id")
                
                if not challenge_id:
                    raise HTTPException(status_code=400, detail="Failed to create MFA challenge")
                
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
                    raise HTTPException(status_code=400, detail="Invalid verification code")
            
            return MessageResponse(
                success=True,
                message="MFA enrollment verified successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"MFA verify enrollment error: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"Invalid verification code")

    @staticmethod
    async def mfa_list_factors(user_id: str) -> MFAListResponse:
        """
        List all MFA factors for a user
        
        Args:
            user_id: User's ID
            
        Returns:
            MFAListResponse containing list of factors
        """
        try:
            # Get user ID from token first
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            # Use Admin API to list factors (requires service role key)
            url = os.getenv("SUPABASE_URL")
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if not url or not service_key:
                raise HTTPException(status_code=500, detail="Supabase configuration not found")
            
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
                    return MFAListResponse(factors=[])
                
                if response.status_code != 200:
                    print(f"Admin API error: {response.status_code} - {response.text}")
                    raise HTTPException(status_code=400, detail="Failed to list MFA factors")
                
                data = response.json()
                factors = data if isinstance(data, list) else data.get('factors', [])
                
                return MFAListResponse(
                    factors=[
                        MFAFactorResponse(
                            id=f.get("id", ""),
                            type=f.get("factor_type", f.get("type", "")),
                            friendly_name=f.get("friendly_name"),
                            status=f.get("status", "verified")
                        )
                        for f in factors
                    ]
                )
        except HTTPException:
            raise
        except Exception as e:
            print(f"MFA list factors error: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"Failed to list MFA factors: {e}")

    @staticmethod
    async def mfa_unenroll(user_id: str, factor_id: str) -> MessageResponse:
        """
        Unenroll (remove) an MFA factor
        
        Args:
            user_id: User's ID
            factor_id: Factor ID to remove
            
        Returns:
            MessageResponse with success status
        """
        try:
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            # Use Admin API to unenroll MFA factor
            url = os.getenv("SUPABASE_URL")
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if not url or not service_key:
                raise HTTPException(status_code=500, detail="Supabase configuration not found")
            
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
                    raise HTTPException(status_code=400, detail="Failed to remove MFA factor")
            
            return MessageResponse(
                success=True,
                message="MFA factor removed successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"MFA unenroll error: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to remove MFA factor: {e}")

