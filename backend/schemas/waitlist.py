"""
Waitlist Schemas - Pydantic models for waitlist operations
"""

from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional, Union
from datetime import datetime


class WaitlistSignupRequest(BaseModel):
    """Waitlist signup request"""

    email: EmailStr
    name: Optional[str] = None


class WaitlistEntry(BaseModel):
    """Waitlist entry response"""

    id: str
    email: str
    name: Optional[str] = None
    created_at: Union[str, datetime]
    notified_at: Optional[Union[str, datetime]] = None

    @field_serializer("created_at", "notified_at")
    def serialize_datetime(self, value: Union[str, datetime, None]) -> Optional[str]:
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
    entry: Optional[WaitlistEntry] = None
