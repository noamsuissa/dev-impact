"""
GitHub integration client.
Handles GitHub OAuth Device Flow and API calls.
"""

import httpx
from typing import Optional
from fastapi import HTTPException

from backend.core.config import GitHubConfig
from backend.schemas.github_auth import DeviceCodeResponse, TokenResponse, GitHubUser


class GitHubClient:
    """Client for GitHub OAuth Device Flow and API operations."""

    def __init__(self, config: GitHubConfig):
        """
        Initialize GitHub client with configuration.

        Args:
            config: GitHub configuration object
        """
        self.config = config

    async def initiate_device_flow(self) -> DeviceCodeResponse:
        """
        Initiate GitHub Device Flow authentication.
        Returns device code, user code, and verification URI.

        Returns:
            Device code response with verification details

        Raises:
            HTTPException: If device flow initiation fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config.device_auth_url,
                    headers={
                        "Accept": "application/json",
                    },
                    data={
                        "client_id": self.config.client_id,
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
            raise HTTPException(
                status_code=500, detail="Failed to initiate GitHub device flow"
            )

    async def poll_for_token(self, device_code: str) -> Optional[TokenResponse]:
        """
        Poll GitHub for access token.

        Args:
            device_code: Device code from initiate_device_flow

        Returns:
            TokenResponse if authorized, None if still pending

        Raises:
            HTTPException: On error or timeout
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config.token_url,
                    headers={
                        "Accept": "application/json",
                    },
                    data={
                        "client_id": self.config.client_id,
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
            raise HTTPException(
                status_code=500, detail=f"Failed to poll for GitHub token: {e}"
            )

    async def get_user_profile(self, access_token: str) -> GitHubUser:
        """
        Fetch GitHub user profile using access token.

        Args:
            access_token: GitHub OAuth access token

        Returns:
            GitHub user profile information

        Raises:
            HTTPException: If profile fetch fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.config.user_api_url,
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
            raise HTTPException(
                status_code=500, detail=f"Failed to get GitHub user profile: {e}"
            )
