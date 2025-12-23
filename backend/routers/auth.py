"""
Auth Router - Handle authentication endpoints
"""
from fastapi import APIRouter, Header, Depends
from typing import Optional
from backend.schemas.auth import (
    SignUpRequest,
    SignInRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    UpdatePasswordRequest,
    AuthResponse,
    MessageResponse,
    MFAEnrollRequest,
    MFAVerifyRequest,
    MFAEnrollResponse,
    MFAListResponse
)
from backend.services.auth.auth_service import AuthService
from backend.services.auth.mfa_service import MFAService
from backend.utils import auth_utils
from backend.utils.dependencies import ServiceDBClient

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


@router.post("/signup", response_model=AuthResponse)
async def sign_up(request: SignUpRequest, client: ServiceDBClient):
    """
    Sign up a new user
    
    Creates a new user account with email and password.
    May require email verification depending on Supabase settings.
    """
    result = await AuthService.sign_up(client, request.email, request.password)
    return result


@router.post("/signin", response_model=AuthResponse)
async def sign_in(request: SignInRequest, client: ServiceDBClient):
    """
    Sign in an existing user
    
    Authenticates user with email and password.
    If MFA is enabled, returns MFA challenge info instead of session.
    Returns user data and session tokens.
    """
    result = await AuthService.sign_in(
        client,
        request.email, 
        request.password,
        request.mfa_challenge_id,
        request.mfa_code,
        request.mfa_factor_id
    )
    return result


@router.post("/signout", response_model=MessageResponse)
async def sign_out(client: ServiceDBClient, authorization: Optional[str] = Header(None)):
    """
    Sign out current user
    
    Invalidates the user's session.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return {"success": True, "message": "Signed out"}
    
    access_token = authorization.replace("Bearer ", "")
    
    result = await AuthService.sign_out(client, access_token)
    return result

@router.get("/session", response_model=AuthResponse)
async def get_session(client: ServiceDBClient, authorization: str = Depends(auth_utils.get_access_token)):
    """
    Get current session
    
    Returns current user and session data if token is valid.
    """
    result = await auth_utils.get_session(client, authorization)
    return result

@router.post("/refresh", response_model=AuthResponse)
async def refresh_session(request: RefreshTokenRequest, client: ServiceDBClient):
    """
    Refresh user session
    
    Gets a new access token using refresh token.
    """
    result = await auth_utils.refresh_session(client, request.refresh_token)
    return result


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest, client: ServiceDBClient):
    """
    Send password reset email
    
    Sends a password reset link to the user's email.
    """
    result = await AuthService.reset_password_email(client, request.email)
    return result


@router.post("/update-password", response_model=MessageResponse)
async def update_password(
    request: UpdatePasswordRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Update user password
    
    Updates the password for the currently authenticated user.
    Requires valid access token.
    """
    result = await AuthService.update_password(authorization, request.new_password)
    return result


@router.post("/mfa/enroll", response_model=MFAEnrollResponse)
async def mfa_enroll(
    request: MFAEnrollRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Enroll user in MFA (TOTP)
    
    Creates a new TOTP factor and returns QR code for setup.
    Requires valid access token.
    """
    result = await MFAService.mfa_enroll(authorization, request.friendly_name)
    return result


@router.post("/mfa/verify", response_model=MessageResponse)
async def mfa_verify_enrollment(
    request: MFAVerifyRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Verify MFA enrollment with a code
    
    Verifies the TOTP code to complete enrollment.
    Requires valid access token.
    """
    result = await MFAService.mfa_verify_enrollment(authorization, request.factor_id, request.code)
    return result


@router.get("/mfa/factors", response_model=MFAListResponse)
async def mfa_list_factors(client: ServiceDBClient, authorization: str = Depends(auth_utils.get_access_token)):
    """
    List all MFA factors for the current user
    
    Returns list of enrolled MFA factors.
    Requires valid access token.
    """
    user_id = await auth_utils.verify_token(client, authorization)
    result = await MFAService.mfa_list_factors(user_id)
    return result


@router.delete("/mfa/factors/{factor_id}", response_model=MessageResponse)
async def mfa_unenroll(
    factor_id: str,
    client: ServiceDBClient,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Unenroll (remove) an MFA factor
    
    Removes the specified MFA factor from the user's account.
    Requires valid access token.
    """
    user_id = await auth_utils.verify_token(client, authorization)
    result = await MFAService.mfa_unenroll(user_id, factor_id)
    return result

