"""
Auth Schemas - Pydantic models for authentication
"""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional, Union
from datetime import datetime


class SignUpRequest(BaseModel):
    """Sign up request schema"""
    email: EmailStr
    password: str
    captcha_token: Optional[str] = None


class SignInRequest(BaseModel):
    """Sign in request schema"""
    email: EmailStr
    password: str
    mfa_challenge_id: Optional[str] = None
    mfa_code: Optional[str] = None
    mfa_factor_id: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""
    email: EmailStr


class UpdatePasswordRequest(BaseModel):
    """Update password request schema"""
    new_password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    created_at: Union[str, datetime]
    
    @field_serializer('created_at')
    def serialize_created_at(self, value: Union[str, datetime]) -> str:
        """Convert datetime to ISO format string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class SessionResponse(BaseModel):
    """Session response schema"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None


class MFAFactorResponse(BaseModel):
    """MFA factor response schema"""
    id: str
    type: str
    friendly_name: Optional[str] = None
    status: str


class AuthResponse(BaseModel):
    """Authentication response schema"""
    user: Optional[UserResponse] = None
    session: Optional[SessionResponse] = None
    requires_email_verification: Optional[bool] = False
    requires_mfa: Optional[bool] = False
    mfa_challenge_id: Optional[str] = None
    mfa_factor_id: Optional[str] = None
    mfa_factors: Optional[list[MFAFactorResponse]] = None


class MessageResponse(BaseModel):
    """Generic message response"""
    success: bool
    message: str


class MFAEnrollRequest(BaseModel):
    """MFA enroll request schema"""
    friendly_name: Optional[str] = "Authenticator App"


class MFAVerifyRequest(BaseModel):
    """MFA verify enrollment request schema"""
    factor_id: str
    code: str



class MFAEnrollResponse(BaseModel):
    """MFA enroll response schema"""
    id: str
    type: str
    qr_code: str
    secret: str
    friendly_name: Optional[str] = None


class MFAListResponse(BaseModel):
    """MFA list factors response schema"""
    factors: list[MFAFactorResponse]

