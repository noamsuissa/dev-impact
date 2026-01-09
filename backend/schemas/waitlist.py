"""Waitlist Schemas - Pydantic models for waitlist operations"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, field_serializer


class WaitlistSignupRequest(BaseModel):
    """Waitlist signup request"""

    email: EmailStr
    name: str | None = None


class WaitlistEntry(BaseModel):
    """Waitlist entry response"""

    id: str
    email: str
    name: str | None = None
    created_at: str | datetime
    notified_at: str | datetime | None = None

    @field_serializer("created_at", "notified_at")
    def serialize_datetime(self, value: str | datetime | None) -> str | None:
        """Convert datetime to ISO format string"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class WaitlistResponse(BaseModel):
    """Waitlist signup response"""

    success: bool
    message: str
    entry: WaitlistEntry | None = None
