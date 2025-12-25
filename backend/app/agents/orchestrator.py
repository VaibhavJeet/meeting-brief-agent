"""Brief Orchestrator - Coordinates all agents for brief generation."""

from datetime import datetime
from typing import Dict, Any, List, Optional
import time
import uuid

from app.agents.context_gatherer import ContextGathererAgent, GatheredContext
from app.agents.brief_generator import BriefGeneratorAgent, GeneratedBrief
from app.agents.insight_extractor import InsightExtractorAgent, InsightExtractionResult
from app.models.brief import Brief, ParticipantProfile, ActionItem, TalkingPoint, RiskOpportunity


class BriefOrchestrator:
    """Orchestrates the complete brief generation workflow."""

    def __init__(self, mcp_integrations: Optional[Dict[str, Any]] = None):
        self.context_gatherer = ContextGathererAgent(mcp_integrations)
        self.brief_generator = BriefGeneratorAgent()
        self.insight_extractor = InsightExtractorAgent()
        self.mcp = mcp_integrations or {}

    async def generate_brief(
        self,
        meeting_id: str,
        meeting_title: str,
        meeting_date: datetime,
        participants: List[str],
        meeting_description: Optional[str] = None,
        include_email: bool = True,
        include_crm: bool = True,
        include_calendar: bool = True,
        lookback_days: int = 30
    ) -> Brief:
        """Generate a complete meeting brief."""
        start_time = time.time()
        data_sources = []

        # Step 1: Gather context from all sources
        context = await self.context_gatherer.gather(
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            participants=participants,
            meeting_description=meeting_description,
            lookback_days=lookback_days,
            include_email=include_email,
            include_crm=include_crm,
            include_calendar=include_calendar
        )
        data_sources.extend(context.sources_accessed)

        # Step 2: Extract insights from gathered context
        insights = await self.insight_extractor.extract(
            email_threads=context.email_threads,
            meeting_notes=[{
                "date": event.get("start", {}).get("dateTime"),
                "title": event.get("summary", ""),
                "notes": event.get("description", ""),
                "attendees": [a.get("email") for a in event.get("attendees", [])]
            } for event in context.calendar_events],
            context=f"Preparing for meeting: {meeting_title}"
        )

        # Step 3: Generate the brief
        generated = await self.brief_generator.generate(
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            meeting_description=meeting_description,
            context=context
        )

        # Step 4: Combine insights with generated brief
        action_items = self._merge_action_items(
            generated.open_action_items,
            insights.action_items
        )

        talking_points = self._enhance_talking_points(
            generated.talking_points,
            insights
        )

        risks_opportunities = self._merge_risks_opportunities(
            generated.risks_opportunities,
            insights.concerns,
            insights.opportunities
        )

        generation_time = time.time() - start_time

        # Build final brief
        brief = Brief(
            id=str(uuid.uuid4()),
            meeting_id=meeting_id,
            title=f"Brief: {meeting_title}",
            meeting_objective=generated.meeting_objective,
            executive_summary=generated.executive_summary,
            participant_profiles=[
                ParticipantProfile(**p) for p in generated.participant_profiles
            ],
            relationship_timeline=generated.relationship_timeline,
            open_action_items=action_items,
            talking_points=talking_points,
            risks_opportunities=risks_opportunities,
            email_context=generated.email_summary,
            crm_context=self._format_crm_context(context.crm_data),
            previous_meetings_summary=generated.previous_meetings_summary,
            generated_at=datetime.utcnow()
        )

        return brief

    def _merge_action_items(
        self,
        brief_items: List[Dict[str, Any]],
        insight_items: List[Any]
    ) -> List[ActionItem]:
        """Merge action items from brief and insights."""
        items = []
        seen = set()

        for item in brief_items:
            key = item.get("description", "")[:50].lower()
            if key not in seen:
                seen.add(key)
                items.append(ActionItem(
                    description=item.get("description", ""),
                    assignee=item.get("assignee"),
                    due_date=item.get("due_date"),
                    status=item.get("status", "open"),
                    source=item.get("source")
                ))

        for insight in insight_items:
            key = insight.content[:50].lower()
            if key not in seen:
                seen.add(key)
                items.append(ActionItem(
                    description=insight.content,
                    assignee=insight.participants[0] if insight.participants else None,
                    status=insight.status,
                    source=insight.source
                ))

        return items[:10]  # Limit to top 10

    def _enhance_talking_points(
        self,
        points: List[Dict[str, Any]],
        insights: InsightExtractionResult
    ) -> List[TalkingPoint]:
        """Enhance talking points with insights."""
        enhanced = []

        for point in points:
            enhanced.append(TalkingPoint(
                topic=point.get("topic", ""),
                context=point.get("context", ""),
                priority=point.get("priority", "medium"),
                source=point.get("source")
            ))

        # Add talking points from concerns
        for concern in insights.concerns[:3]:
            enhanced.append(TalkingPoint(
                topic=f"Address concern: {concern.content[:50]}",
                context=concern.content,
                priority="high",
                source=concern.source
            ))

        # Add talking points from opportunities
        for opp in insights.opportunities[:2]:
            enhanced.append(TalkingPoint(
                topic=f"Explore opportunity: {opp.content[:50]}",
                context=opp.content,
                priority="medium",
                source=opp.source
            ))

        return enhanced[:8]  # Limit to 8 points

    def _merge_risks_opportunities(
        self,
        existing: List[Dict[str, Any]],
        concerns: List[Any],
        opportunities: List[Any]
    ) -> List[RiskOpportunity]:
        """Merge risks and opportunities."""
        items = []

        for item in existing:
            items.append(RiskOpportunity(
                type=item.get("type", "risk"),
                title=item.get("title", ""),
                description=item.get("description", ""),
                severity=item.get("severity", "medium"),
                recommended_action=item.get("recommended_action")
            ))

        for concern in concerns:
            items.append(RiskOpportunity(
                type="risk",
                title=concern.content[:50],
                description=concern.content,
                severity=concern.priority,
                recommended_action=None
            ))

        for opp in opportunities:
            items.append(RiskOpportunity(
                type="opportunity",
                title=opp.content[:50],
                description=opp.content,
                severity=opp.priority,
                recommended_action=None
            ))

        return items[:6]

    def _format_crm_context(self, crm_data: Dict[str, Any]) -> Optional[str]:
        """Format CRM data into readable context."""
        if not crm_data or not crm_data.get("contacts"):
            return None

        parts = []
        for contact in crm_data.get("contacts", [])[:3]:
            parts.append(
                f"- {contact.get('name', 'Unknown')}: "
                f"{contact.get('title', 'N/A')} at {contact.get('company', 'N/A')}"
            )

        for deal in crm_data.get("deals", [])[:3]:
            parts.append(
                f"- Deal: {deal.get('name', 'Unknown')} - "
                f"Stage: {deal.get('stage', 'N/A')}, Value: {deal.get('value', 'N/A')}"
            )

        return "\n".join(parts) if parts else None
