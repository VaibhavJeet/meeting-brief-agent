"""Insight Extractor Agent - Extracts actionable insights from interactions."""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.core.llm import get_llm


class ExtractedInsight(BaseModel):
    """Single extracted insight."""

    type: str = Field(description="Type: action_item, commitment, decision, concern, opportunity")
    content: str = Field(description="The insight content")
    source: str = Field(description="Source of the insight (email, meeting, etc.)")
    source_date: Optional[str] = Field(default=None, description="Date of the source")
    participants: List[str] = Field(default_factory=list, description="Related participants")
    priority: str = Field(default="medium", description="Priority: high, medium, low")
    status: str = Field(default="open", description="Status: open, in_progress, resolved")
    confidence: float = Field(default=0.8, description="Confidence score 0-1")


class InsightExtractionResult(BaseModel):
    """Result of insight extraction."""

    action_items: List[ExtractedInsight] = Field(default_factory=list)
    commitments: List[ExtractedInsight] = Field(default_factory=list)
    decisions: List[ExtractedInsight] = Field(default_factory=list)
    concerns: List[ExtractedInsight] = Field(default_factory=list)
    opportunities: List[ExtractedInsight] = Field(default_factory=list)
    key_topics: List[str] = Field(default_factory=list)
    sentiment_summary: str = Field(default="neutral")
    relationship_health: str = Field(default="healthy")


class InsightExtractorAgent:
    """Agent that extracts actionable insights from email threads and meeting notes."""

    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=InsightExtractionResult)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting actionable insights from 
business communications. Your job is to identify:

1. **Action Items**: Tasks that need to be done (assigned to someone, has deadline)
2. **Commitments**: Promises made by either party
3. **Decisions**: Important decisions that were made
4. **Concerns**: Issues, problems, or risks mentioned
5. **Opportunities**: Potential opportunities identified

Also analyze:
- Key topics discussed across interactions
- Overall sentiment (positive, neutral, negative)
- Relationship health (healthy, needs attention, at risk)

Be precise and extract only clearly stated or strongly implied insights.
Assign confidence scores based on how explicit the insight is.

{format_instructions}"""),
            ("human", """Extract insights from the following interactions:

{interactions}

Context about the relationship:
{context}

Extract all actionable insights and analyze the overall relationship.""")
        ])

    async def extract_from_emails(
        self,
        email_threads: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> InsightExtractionResult:
        """Extract insights from email threads."""
        
        interactions_text = "\n\n".join([
            f"Email ({thread.get('date', 'Unknown date')}):\n"
            f"From: {thread.get('from', 'Unknown')}\n"
            f"To: {thread.get('to', 'Unknown')}\n"
            f"Subject: {thread.get('subject', 'No subject')}\n"
            f"Body: {thread.get('body', '')[:1000]}"
            for thread in email_threads[:15]
        ])

        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "interactions": interactions_text or "No email data available",
            "context": context or "No additional context",
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            return InsightExtractionResult(**result)
        return result

    async def extract_from_meetings(
        self,
        meeting_notes: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> InsightExtractionResult:
        """Extract insights from meeting notes."""
        
        interactions_text = "\n\n".join([
            f"Meeting ({note.get('date', 'Unknown date')}):\n"
            f"Title: {note.get('title', 'Untitled')}\n"
            f"Attendees: {', '.join(note.get('attendees', []))}\n"
            f"Notes: {note.get('notes', '')[:1500]}"
            for note in meeting_notes[:10]
        ])

        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "interactions": interactions_text or "No meeting data available",
            "context": context or "No additional context",
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            return InsightExtractionResult(**result)
        return result

    async def extract(
        self,
        email_threads: List[Dict[str, Any]] = None,
        meeting_notes: List[Dict[str, Any]] = None,
        context: Optional[str] = None
    ) -> InsightExtractionResult:
        """Extract insights from all available sources."""
        
        all_interactions = []
        
        if email_threads:
            for thread in email_threads[:15]:
                all_interactions.append(
                    f"Email ({thread.get('date', 'Unknown')}):\n"
                    f"From: {thread.get('from', 'Unknown')} To: {thread.get('to', 'Unknown')}\n"
                    f"Subject: {thread.get('subject', '')}\n"
                    f"{thread.get('body', '')[:800]}"
                )
        
        if meeting_notes:
            for note in meeting_notes[:10]:
                all_interactions.append(
                    f"Meeting ({note.get('date', 'Unknown')}):\n"
                    f"Title: {note.get('title', 'Untitled')}\n"
                    f"{note.get('notes', '')[:1000]}"
                )

        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "interactions": "\n\n---\n\n".join(all_interactions) if all_interactions else "No interaction data available",
            "context": context or "No additional context provided",
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            return InsightExtractionResult(**result)
        return result
