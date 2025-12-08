from pydantic import BaseModel
from typing import Optional


class DeviceCodeResponse(BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int


class PollRequest(BaseModel):
    device_code: str


class TokenResponse(BaseModel):
    status: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    scope: Optional[str] = None


class GitHubUser(BaseModel):
    login: str
    avatar_url: str
    name: Optional[str] = None
    email: Optional[str] = None


class UserProfileRequest(BaseModel):
    access_token: str

