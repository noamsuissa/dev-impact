"""
Auth Schemas - Pydantic models for authentication
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, field_serializer


class SignUpRequest(BaseModel):
    """Sign up request schema"""

    email: EmailStr
    password: str


class SignInRequest(BaseModel):
    """Sign in request schema"""

    email: EmailStr
    password: str
    mfa_challenge_id: str | None = None
    mfa_code: str | None = None
    mfa_factor_id: str | None = None


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
    created_at: str | datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: str | datetime) -> str:
        """Convert datetime to ISO format string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class SessionResponse(BaseModel):
    """Session response schema"""

    access_token: str
    refresh_token: str | None = None
    expires_at: int | None = None


class MFAFactorResponse(BaseModel):
    """MFA factor response schema"""

    id: str
    type: str
    friendly_name: str | None = None
    status: str


class AuthResponse(BaseModel):
    """Authentication response schema"""

    user: UserResponse | None = None
    session: SessionResponse | None = None
    requires_email_verification: bool | None = False
    requires_mfa: bool | None = False
    mfa_challenge_id: str | None = None
    mfa_factor_id: str | None = None
    mfa_factors: list[MFAFactorResponse] | None = None


class MessageResponse(BaseModel):
    """Generic message response"""

    success: bool
    message: str


class MFAEnrollRequest(BaseModel):
    """MFA enroll request schema"""

    friendly_name: str | None = "Authenticator App"


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
    friendly_name: str | None = None


class MFAListResponse(BaseModel):
    """MFA list factors response schema"""

    factors: list[MFAFactorResponse]
