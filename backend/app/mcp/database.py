"""Database MCP integration."""

from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.mcp.base import BaseMCPIntegration, MCPConfig
from app.models.db_models import MeetingDB, BriefDB, ContactDB, InteractionDB


class DatabaseMCP(BaseMCPIntegration):
    """Database MCP for storing and retrieving meeting data."""

    name = "database"
    description = "Database integration for meetings, briefs, and contacts"

    def __init__(self, config: MCPConfig, session: AsyncSession = None):
        super().__init__(config)
        self._session = session

    def set_session(self, session: AsyncSession):
        """Set database session."""
        self._session = session

    async def connect(self) -> bool:
        """Connect to database."""
        self._connected = self._session is not None
        return self._connected

    async def disconnect(self) -> None:
        """Disconnect from database."""
        self._session = None
        self._connected = False

    async def health_check(self) -> Dict[str, Any]:
        """Check database connection health."""
        return {
            "connected": self._connected,
            "provider": "sqlalchemy",
            "status": "healthy" if self._connected else "disconnected"
        }

    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute database action."""
        actions = {
            "get_meeting": self.get_meeting,
            "list_meetings": self.list_meetings,
            "save_meeting": self.save_meeting,
            "get_brief": self.get_brief,
            "save_brief": self.save_brief,
            "get_contact": self.get_contact,
            "get_contact_by_email": self.get_contact_by_email,
            "save_contact": self.save_contact,
            "get_interactions": self.get_interactions,
            "save_interaction": self.save_interaction,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return await actions[action](**params)

    async def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by ID."""
        if not self._session:
            return None

        result = await self._session.execute(
            select(MeetingDB).where(MeetingDB.id == meeting_id)
        )
        meeting = result.scalar_one_or_none()

        if meeting:
            return {
                "id": meeting.id,
                "title": meeting.title,
                "description": meeting.description,
                "start_time": meeting.start_time.isoformat(),
                "end_time": meeting.end_time.isoformat(),
                "location": meeting.location,
                "participants": meeting.participants,
                "is_recurring": meeting.is_recurring
            }
        return None

    async def list_meetings(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List meetings within date range."""
        if not self._session:
            return []

        query = select(MeetingDB)

        if start_date:
            query = query.where(MeetingDB.start_time >= start_date)
        if end_date:
            query = query.where(MeetingDB.start_time <= end_date)

        query = query.order_by(MeetingDB.start_time.desc()).limit(limit)

        result = await self._session.execute(query)
        meetings = result.scalars().all()

        return [{
            "id": m.id,
            "title": m.title,
            "start_time": m.start_time.isoformat(),
            "end_time": m.end_time.isoformat(),
            "participants": m.participants
        } for m in meetings]

    async def save_meeting(self, meeting_data: Dict[str, Any]) -> str:
        """Save meeting to database."""
        if not self._session:
            raise RuntimeError("No database session")

        meeting = MeetingDB(
            id=meeting_data.get("id"),
            title=meeting_data["title"],
            description=meeting_data.get("description"),
            start_time=meeting_data["start_time"],
            end_time=meeting_data["end_time"],
            location=meeting_data.get("location"),
            meeting_link=meeting_data.get("meeting_link"),
            participants=meeting_data.get("participants", []),
            calendar_id=meeting_data.get("calendar_id"),
            is_recurring=meeting_data.get("is_recurring", False)
        )

        self._session.add(meeting)
        await self._session.commit()
        await self._session.refresh(meeting)

        return meeting.id

    async def get_brief(self, brief_id: str) -> Optional[Dict[str, Any]]:
        """Get brief by ID."""
        if not self._session:
            return None

        result = await self._session.execute(
            select(BriefDB).where(BriefDB.id == brief_id)
        )
        brief = result.scalar_one_or_none()

        if brief:
            return {
                "id": brief.id,
                "meeting_id": brief.meeting_id,
                "title": brief.title,
                "executive_summary": brief.executive_summary,
                "participant_profiles": brief.participant_profiles,
                "talking_points": brief.talking_points,
                "risks_opportunities": brief.risks_opportunities,
                "generated_at": brief.generated_at.isoformat()
            }
        return None

    async def save_brief(self, brief_data: Dict[str, Any]) -> str:
        """Save brief to database."""
        if not self._session:
            raise RuntimeError("No database session")

        brief = BriefDB(
            id=brief_data.get("id"),
            meeting_id=brief_data["meeting_id"],
            title=brief_data["title"],
            meeting_objective=brief_data.get("meeting_objective"),
            executive_summary=brief_data["executive_summary"],
            participant_profiles=brief_data.get("participant_profiles", []),
            relationship_timeline=brief_data.get("relationship_timeline", []),
            open_action_items=brief_data.get("open_action_items", []),
            talking_points=brief_data.get("talking_points", []),
            risks_opportunities=brief_data.get("risks_opportunities", []),
            email_context=brief_data.get("email_context"),
            crm_context=brief_data.get("crm_context"),
            previous_meetings_summary=brief_data.get("previous_meetings_summary"),
            generation_time_seconds=brief_data.get("generation_time_seconds", 0),
            data_sources_used=brief_data.get("data_sources_used", [])
        )

        self._session.add(brief)
        await self._session.commit()
        await self._session.refresh(brief)

        return brief.id

    async def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact by ID."""
        if not self._session:
            return None

        result = await self._session.execute(
            select(ContactDB).where(ContactDB.id == contact_id)
        )
        contact = result.scalar_one_or_none()

        if contact:
            return {
                "id": contact.id,
                "email": contact.email,
                "name": contact.name,
                "title": contact.title,
                "company": contact.company,
                "phone": contact.phone,
                "tags": contact.tags
            }
        return None

    async def get_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get contact by email."""
        if not self._session:
            return None

        result = await self._session.execute(
            select(ContactDB).where(ContactDB.email == email)
        )
        contact = result.scalar_one_or_none()

        if contact:
            return {
                "id": contact.id,
                "email": contact.email,
                "name": contact.name,
                "title": contact.title,
                "company": contact.company
            }
        return None

    async def save_contact(self, contact_data: Dict[str, Any]) -> str:
        """Save contact to database."""
        if not self._session:
            raise RuntimeError("No database session")

        contact = ContactDB(
            id=contact_data.get("id"),
            email=contact_data["email"],
            name=contact_data.get("name"),
            title=contact_data.get("title"),
            company=contact_data.get("company"),
            phone=contact_data.get("phone"),
            linkedin_url=contact_data.get("linkedin_url"),
            tags=contact_data.get("tags", []),
            custom_fields=contact_data.get("custom_fields", {})
        )

        self._session.add(contact)
        await self._session.commit()
        await self._session.refresh(contact)

        return contact.id

    async def get_interactions(
        self,
        contact_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get interactions for a contact."""
        if not self._session:
            return []

        result = await self._session.execute(
            select(InteractionDB)
            .where(InteractionDB.contact_id == contact_id)
            .order_by(InteractionDB.date.desc())
            .limit(limit)
        )
        interactions = result.scalars().all()

        return [{
            "id": i.id,
            "type": i.type,
            "date": i.date.isoformat(),
            "summary": i.summary,
            "sentiment": i.sentiment,
            "key_topics": i.key_topics
        } for i in interactions]

    async def save_interaction(self, interaction_data: Dict[str, Any]) -> str:
        """Save interaction to database."""
        if not self._session:
            raise RuntimeError("No database session")

        interaction = InteractionDB(
            id=interaction_data.get("id"),
            contact_id=interaction_data["contact_id"],
            type=interaction_data["type"],
            date=interaction_data["date"],
            summary=interaction_data["summary"],
            sentiment=interaction_data.get("sentiment"),
            key_topics=interaction_data.get("key_topics", []),
            participants=interaction_data.get("participants", []),
            raw_data=interaction_data.get("raw_data", {})
        )

        self._session.add(interaction)
        await self._session.commit()
        await self._session.refresh(interaction)

        return interaction.id

    def get_available_actions(self) -> List[str]:
        """Get available database actions."""
        return [
            "get_meeting", "list_meetings", "save_meeting",
            "get_brief", "save_brief",
            "get_contact", "get_contact_by_email", "save_contact",
            "get_interactions", "save_interaction"
        ]
