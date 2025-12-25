"""Brief Generator Agent - Creates comprehensive meeting briefs."""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import uuid

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.core.llm import get_llm
from app.agents.context_gatherer import GatheredContext


class GeneratedBrief(BaseModel):
    """Generated meeting brief."""

    meeting_objective: str = Field(description="Inferred objective of the meeting")
    executive_summary: str = Field(description="2-3 sentence executive summary")
    participant_profiles: List[Dict[str, Any]] = Field(
        description="Profile for each participant with background and key topics"
    )
    relationship_timeline: List[Dict[str, Any]] = Field(
        description="Timeline of key interactions and milestones"
    )
    open_action_items: List[Dict[str, Any]] = Field(
        description="Pending action items from past interactions"
    )
    talking_points: List[Dict[str, Any]] = Field(
        description="Suggested talking points prioritized by importance"
    )
    risks_opportunities: List[Dict[str, Any]] = Field(
        description="Key risks and opportunities to be aware of"
    )
    email_summary: Optional[str] = Field(
        default=None, description="Summary of recent email exchanges"
    )
    previous_meetings_summary: Optional[str] = Field(
        default=None, description="Summary of previous meetings with participants"
    )


class BriefGeneratorAgent:
    """Agent that generates comprehensive meeting briefs from gathered context."""

    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=GeneratedBrief)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert executive assistant specializing in creating 
comprehensive, actionable meeting briefs. Your briefs help professionals walk into 
meetings fully prepared with all relevant context.

Your briefs should:
1. Start with a clear executive summary
2. Provide context on each participant
3. Highlight relationship history and key milestones
4. Surface any open action items or commitments
5. Suggest talking points based on context
6. Flag potential risks and opportunities

Prioritize information by relevance and actionability. Be concise but thorough.
Use professional language suitable for executive consumption.

{format_instructions}"""),
            ("human", """Generate a meeting brief for:

Meeting: {meeting_title}
Date/Time: {meeting_date}
Description: {meeting_description}

Gathered Context:
{context}

Create a comprehensive brief that will help the user prepare for this meeting.""")
        ])

    async def generate(
        self,
        meeting_title: str,
        meeting_date: datetime,
        meeting_description: Optional[str],
        context: GatheredContext
    ) -> GeneratedBrief:
        """Generate a meeting brief from gathered context."""
        
        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "meeting_title": meeting_title,
            "meeting_date": meeting_date.isoformat(),
            "meeting_description": meeting_description or "No description provided",
            "context": json.dumps({
                "email_threads": context.email_threads[:10],
                "calendar_events": context.calendar_events[:10],
                "crm_data": context.crm_data,
                "past_interactions": context.past_interactions[:20],
                "participant_profiles": context.participant_profiles,
                "data_quality_score": context.data_quality_score,
                "sources_accessed": context.sources_accessed
            }, indent=2),
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            return GeneratedBrief(**result)
        return result


class BriefRefinerAgent:
    """Agent that refines and improves generated briefs based on feedback."""

    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=GeneratedBrief)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at refining and improving meeting briefs.
Your job is to take an existing brief and improve it based on feedback.

When refining:
1. Maintain the overall structure
2. Incorporate the feedback thoughtfully
3. Improve clarity and actionability
4. Ensure nothing important is lost

{format_instructions}"""),
            ("human", """Current Brief:
{current_brief}

Feedback:
{feedback}

Please refine the brief based on this feedback.""")
        ])

    async def refine(
        self,
        current_brief: GeneratedBrief,
        feedback: str
    ) -> GeneratedBrief:
        """Refine a brief based on feedback."""
        
        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "current_brief": current_brief.model_dump_json(indent=2),
            "feedback": feedback,
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            return GeneratedBrief(**result)
        return result
