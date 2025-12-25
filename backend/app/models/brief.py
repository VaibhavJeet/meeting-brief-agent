"""Brief models."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ParticipantProfile(BaseModel):
    """Participant profile in brief."""

    email: str
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    linkedin_url: Optional[str] = None
    recent_interactions: List[str] = Field(default_factory=list)
    key_topics: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = None  # positive, neutral, negative


class ActionItem(BaseModel):
    """Open action item."""

    description: str
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "open"  # open, in_progress, completed
    source: Optional[str] = None  # email, meeting, crm


class TalkingPoint(BaseModel):
    """Suggested talking point."""

    topic: str
    context: str
    priority: str = "medium"  # high, medium, low
    source: Optional[str] = None


class RiskOpportunity(BaseModel):
    """Risk or opportunity highlight."""

    type: str  # risk, opportunity
    title: str
    description: str
    severity: str = "medium"  # high, medium, low
    recommended_action: Optional[str] = None


class Brief(BaseModel):
    """Meeting brief model."""

    id: str
    meeting_id: str
    title: str
    meeting_objective: Optional[str] = None
    executive_summary: str
    participant_profiles: List[ParticipantProfile] = Field(default_factory=list)
    relationship_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    open_action_items: List[ActionItem] = Field(default_factory=list)
    talking_points: List[TalkingPoint] = Field(default_factory=list)
    risks_opportunities: List[RiskOpportunity] = Field(default_factory=list)
    email_context: Optional[str] = None
    crm_context: Optional[str] = None
    previous_meetings_summary: Optional[str] = None
    generated_at: datetime


class BriefCreate(BaseModel):
    """Brief creation request."""

    meeting_id: str
    include_email_context: bool = True
    include_crm_data: bool = True
    include_past_meetings: bool = True
    lookback_days: int = 30


class BriefResponse(Brief):
    """Brief response with metadata."""

    created_at: datetime
    updated_at: datetime
    generation_time_seconds: float
    data_sources_used: List[str] = Field(default_factory=list)
