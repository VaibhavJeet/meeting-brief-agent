"""Meetings API routes."""

from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.meeting import Meeting, MeetingCreate, MeetingResponse, Participant
from app.models.db_models import MeetingDB, BriefDB
from app.agents.orchestrator import BriefOrchestrator

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("", response_model=List[MeetingResponse])
async def list_meetings(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List upcoming meetings."""
    query = select(MeetingDB)

    if start_date:
        query = query.where(MeetingDB.start_time >= start_date)
    if end_date:
        query = query.where(MeetingDB.start_time <= end_date)

    query = query.order_by(MeetingDB.start_time.asc()).limit(limit)

    result = await db.execute(query)
    meetings = result.scalars().all()

    responses = []
    for meeting in meetings:
        # Check if brief exists
        brief_result = await db.execute(
            select(BriefDB.id).where(BriefDB.meeting_id == meeting.id).limit(1)
        )
        brief = brief_result.scalar_one_or_none()

        responses.append(MeetingResponse(
            id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            location=meeting.location,
            meeting_link=meeting.meeting_link,
            participants=[Participant(**p) for p in meeting.participants] if meeting.participants else [],
            calendar_id=meeting.calendar_id,
            is_recurring=meeting.is_recurring,
            recurrence_rule=meeting.recurrence_rule,
            has_brief=brief is not None,
            brief_id=brief,
            created_at=meeting.created_at,
            updated_at=meeting.updated_at
        ))

    return responses


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get meeting details."""
    result = await db.execute(
        select(MeetingDB).where(MeetingDB.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Check if brief exists
    brief_result = await db.execute(
        select(BriefDB.id).where(BriefDB.meeting_id == meeting.id).limit(1)
    )
    brief = brief_result.scalar_one_or_none()

    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        description=meeting.description,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        location=meeting.location,
        meeting_link=meeting.meeting_link,
        participants=[Participant(**p) for p in meeting.participants] if meeting.participants else [],
        calendar_id=meeting.calendar_id,
        is_recurring=meeting.is_recurring,
        recurrence_rule=meeting.recurrence_rule,
        has_brief=brief is not None,
        brief_id=brief,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at
    )


@router.post("", response_model=MeetingResponse)
async def create_meeting(
    meeting: MeetingCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new meeting."""
    meeting_id = str(uuid.uuid4())

    db_meeting = MeetingDB(
        id=meeting_id,
        title=meeting.title,
        description=meeting.description,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        location=meeting.location,
        participants=[{"email": p, "is_organizer": False} for p in meeting.participants]
    )

    db.add(db_meeting)
    await db.commit()
    await db.refresh(db_meeting)

    return MeetingResponse(
        id=db_meeting.id,
        title=db_meeting.title,
        description=db_meeting.description,
        start_time=db_meeting.start_time,
        end_time=db_meeting.end_time,
        location=db_meeting.location,
        participants=[Participant(**p) for p in db_meeting.participants] if db_meeting.participants else [],
        has_brief=False,
        created_at=db_meeting.created_at,
        updated_at=db_meeting.updated_at
    )


@router.post("/{meeting_id}/brief")
async def generate_meeting_brief(
    meeting_id: str,
    include_email: bool = Query(True),
    include_crm: bool = Query(True),
    include_calendar: bool = Query(True),
    lookback_days: int = Query(30, le=90),
    db: AsyncSession = Depends(get_db)
):
    """Generate a brief for a meeting."""
    # Get meeting
    result = await db.execute(
        select(MeetingDB).where(MeetingDB.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Extract participant emails
    participants = [p.get("email") for p in meeting.participants if p.get("email")]

    # Generate brief
    orchestrator = BriefOrchestrator()
    brief = await orchestrator.generate_brief(
        meeting_id=meeting_id,
        meeting_title=meeting.title,
        meeting_date=meeting.start_time,
        participants=participants,
        meeting_description=meeting.description,
        include_email=include_email,
        include_crm=include_crm,
        include_calendar=include_calendar,
        lookback_days=lookback_days
    )

    # Save brief to database
    db_brief = BriefDB(
        id=brief.id,
        meeting_id=meeting_id,
        title=brief.title,
        meeting_objective=brief.meeting_objective,
        executive_summary=brief.executive_summary,
        participant_profiles=[p.model_dump() for p in brief.participant_profiles],
        relationship_timeline=brief.relationship_timeline,
        open_action_items=[a.model_dump() for a in brief.open_action_items],
        talking_points=[t.model_dump() for t in brief.talking_points],
        risks_opportunities=[r.model_dump() for r in brief.risks_opportunities],
        email_context=brief.email_context,
        crm_context=brief.crm_context,
        previous_meetings_summary=brief.previous_meetings_summary,
        generated_at=brief.generated_at
    )

    db.add(db_brief)
    await db.commit()

    return {
        "brief_id": brief.id,
        "meeting_id": meeting_id,
        "title": brief.title,
        "executive_summary": brief.executive_summary,
        "generated_at": brief.generated_at.isoformat()
    }


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a meeting."""
    result = await db.execute(
        select(MeetingDB).where(MeetingDB.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    await db.delete(meeting)
    await db.commit()

    return {"deleted": True, "meeting_id": meeting_id}
