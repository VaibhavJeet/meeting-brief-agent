"""Meeting models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Participant(BaseModel):
    """Meeting participant."""

    email: str
    name: Optional[str] = None
    role: Optional[str] = None
    is_organizer: bool = False


class Meeting(BaseModel):
    """Meeting model."""

    id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    participants: List[Participant] = Field(default_factory=list)
    calendar_id: Optional[str] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None


class MeetingCreate(BaseModel):
    """Meeting creation model."""

    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    participants: List[str] = Field(default_factory=list)  # Email addresses


class MeetingResponse(Meeting):
    """Meeting response with additional fields."""

    has_brief: bool = False
    brief_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
