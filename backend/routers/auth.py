"""
Auth Router - Handle authentication endpoints
"""
from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from schemas.auth import (
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
from services.auth.auth_service import AuthService
from services.auth.mfa_service import MFAService
from utils import auth_utils

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


@router.post("/signup", response_model=AuthResponse)
async def sign_up(request: SignUpRequest):
    """
    Sign up a new user
    
    Creates a new user account with email and password.
    May require email verification depending on Supabase settings.
    """
    try:
        # Pass captcha_token (can be None or bypass string)
        result = await AuthService.sign_up(request.email, request.password, request.captcha_token)
        return AuthResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Sign up error: {e}")
        raise HTTPException(
            status_code=400,
            detail="Failed to create account"
        )


@router.post("/signin", response_model=AuthResponse)
async def sign_in(request: SignInRequest):
    """
    Sign in an existing user
    
    Authenticates user with email and password.
    If MFA is enabled, returns MFA challenge info instead of session.
    Returns user data and session tokens.
    """
    try:
        result = await AuthService.sign_in(
            request.email, 
            request.password,
            request.mfa_challenge_id,
            request.mfa_code,
            request.mfa_factor_id
        )
        return AuthResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Sign in error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


@router.post("/signout", response_model=MessageResponse)
async def sign_out(authorization: Optional[str] = Header(None)):
    """
    Sign out current user
    
    Invalidates the user's session.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return {"success": True, "message": "Signed out"}
    
    access_token = authorization.replace("Bearer ", "")
    
    try:
        result = await AuthService.sign_out(access_token)
        return MessageResponse(**result)
    except Exception as e:
        print(f"Sign out error: {e}")
        return {"success": True, "message": "Signed out"}


@router.get("/session", response_model=AuthResponse)
async def get_session(authorization: str = Depends(auth_utils.get_access_token)):
    """
    Get current session
    
    Returns current user and session data if token is valid.
    """
    try:
        result = await auth_utils.get_session(authorization)
        return AuthResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get session error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_session(request: RefreshTokenRequest):
    """
    Refresh user session
    
    Gets a new access token using refresh token.
    """
    try:
        result = await auth_utils.refresh_session(request.refresh_token)
        return AuthResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Refresh session error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Send password reset email
    
    Sends a password reset link to the user's email.
    """
    try:
        result = await AuthService.reset_password_email(request.email)
        return MessageResponse(**result)
    except Exception as e:
        print(f"Reset password error: {e}")
        return {
            "success": True,
            "message": "If an account exists, a password reset email has been sent"
        }


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
    try:
        result = await AuthService.update_password(authorization, request.new_password)
        return MessageResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update password error: {e}")
        raise HTTPException(
            status_code=400,
            detail="Failed to update password"
        )


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
    try:
        result = await MFAService.mfa_enroll(authorization, request.friendly_name)
        return MFAEnrollResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"MFA enroll error: {e}")
        raise HTTPException(
            status_code=400,
            detail="Failed to enroll in MFA"
        )


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
    try:
        result = await MFAService.mfa_verify_enrollment(authorization, request.factor_id, request.code)
        return MessageResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"MFA verify error: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code"
        )


@router.get("/mfa/factors", response_model=MFAListResponse)
async def mfa_list_factors(authorization: str = Depends(auth_utils.get_access_token)):
    """
    List all MFA factors for the current user
    
    Returns list of enrolled MFA factors.
    Requires valid access token.
    """
    try:
        result = await MFAService.mfa_list_factors(authorization)
        return MFAListResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"MFA list factors error: {e}")
        raise HTTPException(
            status_code=400,
            detail="Failed to list MFA factors"
        )


@router.delete("/mfa/factors/{factor_id}", response_model=MessageResponse)
async def mfa_unenroll(
    factor_id: str,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """
    Unenroll (remove) an MFA factor
    
    Removes the specified MFA factor from the user's account.
    Requires valid access token.
    """
    try:
        result = await MFAService.mfa_unenroll(authorization, factor_id)
        return MessageResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"MFA unenroll error: {e}")
        raise HTTPException(
            status_code=400,
            detail="Failed to remove MFA factor"
        )

