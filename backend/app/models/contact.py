"""Contact models."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Interaction(BaseModel):
    """Contact interaction."""

    id: str
    type: str  # email, meeting, call, note
    date: datetime
    summary: str
    sentiment: Optional[str] = None
    key_topics: List[str] = Field(default_factory=list)
    participants: List[str] = Field(default_factory=list)


class Contact(BaseModel):
    """Contact model."""

    id: str
    email: str
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    crm_id: Optional[str] = None
    crm_provider: Optional[str] = None


class ContactCreate(BaseModel):
    """Contact creation model."""

    email: str
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class ContactResponse(Contact):
    """Contact response with history."""

    total_interactions: int = 0
    last_interaction: Optional[datetime] = None
    first_interaction: Optional[datetime] = None
    interaction_frequency: Optional[str] = None  # daily, weekly, monthly, rarely
    relationship_strength: Optional[str] = None  # strong, moderate, weak
    created_at: datetime
    updated_at: datetime
