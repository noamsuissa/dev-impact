"""GitHub Auth Schemas - Pydantic models for GitHub authentication operations"""

from pydantic import BaseModel


class DeviceCodeResponse(BaseModel):
    """Device code response schema"""

    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int


class PollRequest(BaseModel):
    """Poll request schema"""

    device_code: str


class TokenResponse(BaseModel):
    """Token response schema"""

    status: str
    access_token: str | None = None
    token_type: str | None = None
    scope: str | None = None


class GitHubUser(BaseModel):
    """GitHub user schema"""

    login: str
    avatar_url: str
    name: str | None = None
    email: str | None = None


class UserProfileRequest(BaseModel):
    """User profile request schema"""

    access_token: str
