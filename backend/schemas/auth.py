"""
Auth Schemas - Pydantic models for authentication
"""
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


class AuthResponse(BaseModel):
    """Authentication response schema"""
    user: UserResponse
    session: Optional[SessionResponse] = None
    requires_email_verification: Optional[bool] = False


class MessageResponse(BaseModel):
    """Generic message response"""
    success: bool
    message: str

