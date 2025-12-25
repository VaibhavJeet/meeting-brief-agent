"""Briefs API routes."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.brief import Brief, BriefResponse, ParticipantProfile, ActionItem, TalkingPoint, RiskOpportunity
from app.models.db_models import BriefDB, MeetingDB

router = APIRouter(prefix="/briefs", tags=["briefs"])


@router.get("", response_model=List[BriefResponse])
async def list_briefs(
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all generated briefs."""
    result = await db.execute(
        select(BriefDB)
        .order_by(BriefDB.generated_at.desc())
        .limit(limit)
    )
    briefs = result.scalars().all()

    return [
        BriefResponse(
            id=brief.id,
            meeting_id=brief.meeting_id,
            title=brief.title,
            meeting_objective=brief.meeting_objective,
            executive_summary=brief.executive_summary,
            participant_profiles=[ParticipantProfile(**p) for p in brief.participant_profiles] if brief.participant_profiles else [],
            relationship_timeline=brief.relationship_timeline or [],
            open_action_items=[ActionItem(**a) for a in brief.open_action_items] if brief.open_action_items else [],
            talking_points=[TalkingPoint(**t) for t in brief.talking_points] if brief.talking_points else [],
            risks_opportunities=[RiskOpportunity(**r) for r in brief.risks_opportunities] if brief.risks_opportunities else [],
            email_context=brief.email_context,
            crm_context=brief.crm_context,
            previous_meetings_summary=brief.previous_meetings_summary,
            generated_at=brief.generated_at,
            created_at=brief.created_at,
            updated_at=brief.updated_at,
            generation_time_seconds=brief.generation_time_seconds or 0,
            data_sources_used=brief.data_sources_used or []
        )
        for brief in briefs
    ]


@router.get("/{brief_id}", response_model=BriefResponse)
async def get_brief(
    brief_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get brief details."""
    result = await db.execute(
        select(BriefDB).where(BriefDB.id == brief_id)
    )
    brief = result.scalar_one_or_none()

    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    return BriefResponse(
        id=brief.id,
        meeting_id=brief.meeting_id,
        title=brief.title,
        meeting_objective=brief.meeting_objective,
        executive_summary=brief.executive_summary,
        participant_profiles=[ParticipantProfile(**p) for p in brief.participant_profiles] if brief.participant_profiles else [],
        relationship_timeline=brief.relationship_timeline or [],
        open_action_items=[ActionItem(**a) for a in brief.open_action_items] if brief.open_action_items else [],
        talking_points=[TalkingPoint(**t) for t in brief.talking_points] if brief.talking_points else [],
        risks_opportunities=[RiskOpportunity(**r) for r in brief.risks_opportunities] if brief.risks_opportunities else [],
        email_context=brief.email_context,
        crm_context=brief.crm_context,
        previous_meetings_summary=brief.previous_meetings_summary,
        generated_at=brief.generated_at,
        created_at=brief.created_at,
        updated_at=brief.updated_at,
        generation_time_seconds=brief.generation_time_seconds or 0,
        data_sources_used=brief.data_sources_used or []
    )


@router.put("/{brief_id}")
async def update_brief(
    brief_id: str,
    updates: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update a brief."""
    result = await db.execute(
        select(BriefDB).where(BriefDB.id == brief_id)
    )
    brief = result.scalar_one_or_none()

    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    # Update allowed fields
    allowed_fields = ["title", "meeting_objective", "executive_summary", "talking_points"]
    for field in allowed_fields:
        if field in updates:
            setattr(brief, field, updates[field])

    brief.updated_at = datetime.utcnow()
    await db.commit()

    return {"updated": True, "brief_id": brief_id}


@router.delete("/{brief_id}")
async def delete_brief(
    brief_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a brief."""
    result = await db.execute(
        select(BriefDB).where(BriefDB.id == brief_id)
    )
    brief = result.scalar_one_or_none()

    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    await db.delete(brief)
    await db.commit()

    return {"deleted": True, "brief_id": brief_id}


@router.get("/{brief_id}/export")
async def export_brief(
    brief_id: str,
    format: str = Query("markdown", regex="^(markdown|json|pdf)$"),
    db: AsyncSession = Depends(get_db)
):
    """Export brief in different formats."""
    result = await db.execute(
        select(BriefDB).where(BriefDB.id == brief_id)
    )
    brief = result.scalar_one_or_none()

    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    if format == "markdown":
        content = _generate_markdown(brief)
        return {"format": "markdown", "content": content}
    elif format == "json":
        return {
            "format": "json",
            "content": {
                "title": brief.title,
                "executive_summary": brief.executive_summary,
                "participant_profiles": brief.participant_profiles,
                "talking_points": brief.talking_points,
                "risks_opportunities": brief.risks_opportunities
            }
        }
    else:
        raise HTTPException(status_code=400, detail="PDF export not yet implemented")


def _generate_markdown(brief: BriefDB) -> str:
    """Generate markdown export of brief."""
    lines = [
        f"# {brief.title}",
        "",
        f"*Generated: {brief.generated_at.strftime('%Y-%m-%d %H:%M')}*",
        "",
        "## Executive Summary",
        "",
        brief.executive_summary,
        "",
    ]

    if brief.meeting_objective:
        lines.extend([
            "## Meeting Objective",
            "",
            brief.meeting_objective,
            "",
        ])

    if brief.participant_profiles:
        lines.extend(["## Participants", ""])
        for p in brief.participant_profiles:
            lines.append(f"### {p.get('name', p.get('email', 'Unknown'))}")
            if p.get('title'):
                lines.append(f"*{p.get('title')}*")
            if p.get('company'):
                lines.append(f"Company: {p.get('company')}")
            lines.append("")

    if brief.talking_points:
        lines.extend(["## Talking Points", ""])
        for tp in brief.talking_points:
            priority = tp.get('priority', 'medium')
            lines.append(f"- **[{priority.upper()}]** {tp.get('topic', '')}")
            if tp.get('context'):
                lines.append(f"  - {tp.get('context')}")
        lines.append("")

    if brief.open_action_items:
        lines.extend(["## Open Action Items", ""])
        for ai in brief.open_action_items:
            assignee = f" (@{ai.get('assignee')})" if ai.get('assignee') else ""
            lines.append(f"- [ ] {ai.get('description', '')}{assignee}")
        lines.append("")

    if brief.risks_opportunities:
        lines.extend(["## Risks & Opportunities", ""])
        for ro in brief.risks_opportunities:
            icon = "⚠️" if ro.get('type') == 'risk' else "✨"
            lines.append(f"{icon} **{ro.get('title', '')}**: {ro.get('description', '')}")
        lines.append("")

    return "\n".join(lines)
