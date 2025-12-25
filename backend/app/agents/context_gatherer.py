"""Context Gatherer Agent - Collects context from multiple sources."""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import Tool
from pydantic import BaseModel, Field

from app.core.llm import get_llm


class GatheredContext(BaseModel):
    """Gathered context from all sources."""

    email_threads: List[Dict[str, Any]] = Field(default_factory=list)
    calendar_events: List[Dict[str, Any]] = Field(default_factory=list)
    crm_data: Dict[str, Any] = Field(default_factory=dict)
    past_interactions: List[Dict[str, Any]] = Field(default_factory=list)
    participant_profiles: List[Dict[str, Any]] = Field(default_factory=list)
    data_quality_score: float = 0.0
    sources_accessed: List[str] = Field(default_factory=list)


class ContextGathererAgent:
    """Agent that gathers context from emails, calendar, CRM, and past interactions."""

    def __init__(self, mcp_integrations: Optional[Dict[str, Any]] = None):
        self.llm = get_llm()
        self.mcp = mcp_integrations or {}
        self.parser = JsonOutputParser(pydantic_object=GatheredContext)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a context gathering specialist that collects and organizes 
information from multiple sources to prepare for meeting briefs.

Your responsibilities:
1. Gather relevant email threads with meeting participants
2. Find past calendar events and meetings
3. Retrieve CRM data for contacts
4. Compile interaction history
5. Build participant profiles

Prioritize recent and relevant information. Score data quality based on:
- Completeness of participant profiles
- Recency of interactions
- Relevance to meeting topic

{format_instructions}"""),
            ("human", """Gather context for the following meeting:

Meeting Title: {meeting_title}
Meeting Date: {meeting_date}
Participants: {participants}
Meeting Description: {meeting_description}

Lookback Period: {lookback_days} days

Available Data Sources:
- Emails: {email_data}
- Calendar: {calendar_data}
- CRM: {crm_data}
- Past Interactions: {interaction_data}

Analyze and organize this context for brief generation.""")
        ])

    async def gather_email_context(
        self,
        participants: List[str],
        lookback_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Gather email threads with participants."""
        email_threads = []

        if "email" in self.mcp and self.mcp["email"].get("enabled"):
            # Use MCP email integration
            try:
                since_date = datetime.utcnow() - timedelta(days=lookback_days)
                for participant in participants:
                    threads = await self.mcp["email"]["client"].search_emails(
                        query=f"from:{participant} OR to:{participant}",
                        since=since_date.isoformat()
                    )
                    email_threads.extend(threads)
            except Exception as e:
                print(f"Error fetching emails: {e}")

        return email_threads

    async def gather_calendar_context(
        self,
        participants: List[str],
        lookback_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Gather past calendar events with participants."""
        events = []

        if "calendar" in self.mcp and self.mcp["calendar"].get("enabled"):
            try:
                since_date = datetime.utcnow() - timedelta(days=lookback_days)
                until_date = datetime.utcnow()
                
                calendar_events = await self.mcp["calendar"]["client"].list_events(
                    time_min=since_date.isoformat(),
                    time_max=until_date.isoformat()
                )
                
                # Filter events with matching participants
                for event in calendar_events:
                    event_attendees = [a.get("email", "").lower() for a in event.get("attendees", [])]
                    if any(p.lower() in event_attendees for p in participants):
                        events.append(event)
            except Exception as e:
                print(f"Error fetching calendar events: {e}")

        return events

    async def gather_crm_context(
        self,
        participants: List[str]
    ) -> Dict[str, Any]:
        """Gather CRM data for participants."""
        crm_data = {"contacts": [], "deals": [], "accounts": []}

        if "crm" in self.mcp and self.mcp["crm"].get("enabled"):
            try:
                for participant in participants:
                    contact = await self.mcp["crm"]["client"].get_contact_by_email(participant)
                    if contact:
                        crm_data["contacts"].append(contact)
                        
                        # Get associated deals
                        deals = await self.mcp["crm"]["client"].get_contact_deals(contact["id"])
                        crm_data["deals"].extend(deals)
                        
                        # Get account info
                        if contact.get("account_id"):
                            account = await self.mcp["crm"]["client"].get_account(contact["account_id"])
                            if account:
                                crm_data["accounts"].append(account)
            except Exception as e:
                print(f"Error fetching CRM data: {e}")

        return crm_data

    async def gather(
        self,
        meeting_title: str,
        meeting_date: datetime,
        participants: List[str],
        meeting_description: Optional[str] = None,
        lookback_days: int = 30,
        include_email: bool = True,
        include_crm: bool = True,
        include_calendar: bool = True
    ) -> GatheredContext:
        """Gather all context for a meeting."""
        sources_accessed = []
        
        # Gather from each source
        email_data = []
        if include_email:
            email_data = await self.gather_email_context(participants, lookback_days)
            if email_data:
                sources_accessed.append("email")

        calendar_data = []
        if include_calendar:
            calendar_data = await self.gather_calendar_context(participants, lookback_days)
            if calendar_data:
                sources_accessed.append("calendar")

        crm_data = {}
        if include_crm:
            crm_data = await self.gather_crm_context(participants)
            if crm_data.get("contacts"):
                sources_accessed.append("crm")

        # Use LLM to organize and enrich context
        chain = self.prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "meeting_title": meeting_title,
            "meeting_date": meeting_date.isoformat(),
            "participants": json.dumps(participants),
            "meeting_description": meeting_description or "No description provided",
            "lookback_days": lookback_days,
            "email_data": json.dumps(email_data[:20]) if email_data else "No email data available",
            "calendar_data": json.dumps(calendar_data[:20]) if calendar_data else "No calendar data available",
            "crm_data": json.dumps(crm_data) if crm_data else "No CRM data available",
            "interaction_data": "Derived from above sources",
            "format_instructions": self.parser.get_format_instructions()
        })

        # Ensure result is GatheredContext
        if isinstance(result, dict):
            result["sources_accessed"] = sources_accessed
            return GatheredContext(**result)
        
        result.sources_accessed = sources_accessed
        return result
