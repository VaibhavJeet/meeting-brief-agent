"""SQLAlchemy database models."""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class MeetingDB(Base):
    """Meeting database model."""

    __tablename__ = "meetings"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    meeting_link = Column(String, nullable=True)
    participants = Column(JSON, default=list)
    calendar_id = Column(String, nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    briefs = relationship("BriefDB", back_populates="meeting")


class BriefDB(Base):
    """Brief database model."""

    __tablename__ = "briefs"

    id = Column(String, primary_key=True, default=generate_uuid)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    title = Column(String, nullable=False)
    meeting_objective = Column(Text, nullable=True)
    executive_summary = Column(Text, nullable=False)
    participant_profiles = Column(JSON, default=list)
    relationship_timeline = Column(JSON, default=list)
    open_action_items = Column(JSON, default=list)
    talking_points = Column(JSON, default=list)
    risks_opportunities = Column(JSON, default=list)
    email_context = Column(Text, nullable=True)
    crm_context = Column(Text, nullable=True)
    previous_meetings_summary = Column(Text, nullable=True)
    generation_time_seconds = Column(Float, default=0.0)
    data_sources_used = Column(JSON, default=list)
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meeting = relationship("MeetingDB", back_populates="briefs")


class ContactDB(Base):
    """Contact database model."""

    __tablename__ = "contacts"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    twitter_url = Column(String, nullable=True)
    tags = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)
    crm_id = Column(String, nullable=True)
    crm_provider = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    interactions = relationship("InteractionDB", back_populates="contact")


class InteractionDB(Base):
    """Interaction database model."""

    __tablename__ = "interactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    contact_id = Column(String, ForeignKey("contacts.id"), nullable=False)
    type = Column(String, nullable=False)  # email, meeting, call, note
    date = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=False)
    sentiment = Column(String, nullable=True)
    key_topics = Column(JSON, default=list)
    participants = Column(JSON, default=list)
    raw_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    contact = relationship("ContactDB", back_populates="interactions")
