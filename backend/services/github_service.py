import httpx
from typing import Optional
from ..schemas.github_auth import DeviceCodeResponse, TokenResponse, GitHubUser
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_DEVICE_AUTH_URL = os.getenv("GITHUB_DEVICE_AUTH_URL", "https://github.com/login/device/code")
GITHUB_TOKEN_URL = os.getenv("GITHUB_TOKEN_URL", "https://github.com/login/oauth/access_token")
GITHUB_USER_API_URL = os.getenv("GITHUB_USER_API_URL", "https://api.github.com/user")


class GitHubService:
    """Service for handling GitHub OAuth Device Flow and API calls."""

    @staticmethod
    async def initiate_device_flow() -> DeviceCodeResponse:
        """
        Initiate GitHub Device Flow authentication.
        Returns device code, user code, and verification URI.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GITHUB_DEVICE_AUTH_URL,
                    headers={
                        "Accept": "application/json",
                    },
                    data={
                        "client_id": GITHUB_CLIENT_ID,
                        "scope": "read:user",
                    },
                )
                response.raise_for_status()
                data = response.json()
                
                return DeviceCodeResponse(
                    device_code=data["device_code"],
                    user_code=data["user_code"],
                    verification_uri=data["verification_uri"],
                    expires_in=data["expires_in"],
                    interval=data.get("interval", 5),
                )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to initiate GitHub device flow")

    @staticmethod
    async def poll_for_token(device_code: str) -> Optional[TokenResponse]:
        """
        Poll GitHub for access token.
        Returns TokenResponse if authorized, None if still pending.
        Raises exception on error.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GITHUB_TOKEN_URL,
                    headers={
                        "Accept": "application/json",
                    },
                    data={
                        "client_id": GITHUB_CLIENT_ID,
                        "device_code": device_code,
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    },
                )
                
                data = response.json()
                
                # Check for errors
                if "error" in data:
                    error = data["error"]
                    if error == "authorization_pending":
                        # Still waiting for user authorization
                        return None
                    elif error == "slow_down":
                        # Should increase polling interval (handled by frontend)
                        return None
                    elif error == "expired_token":
                        raise Exception("Device code expired")
                    elif error == "access_denied":
                        raise Exception("User denied authorization")
                    else:
                        raise Exception(f"GitHub OAuth error: {error}")
                
                # Success
                return TokenResponse(
                    status="success",
                    access_token=data["access_token"],
                    token_type=data["token_type"],
                    scope=data["scope"],
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to poll for GitHub token: {e}")
    
    @staticmethod
    async def get_user_profile(access_token: str) -> GitHubUser:
        """
        Fetch GitHub user profile using access token.
        Returns user profile information.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    GITHUB_USER_API_URL,
                    headers={
                        "Accept": "application/json",
                        "Authorization": f"Bearer {access_token}",
                    },
                )
                response.raise_for_status()
                data = response.json()
                
                return GitHubUser(
                    login=data["login"],
                    avatar_url=data["avatar_url"],
                    name=data.get("name"),
                    email=data.get("email"),
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get GitHub user profile: {e}")