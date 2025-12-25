"""Calendar MCP integration for Google Calendar and Outlook."""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

from app.mcp.base import BaseMCPIntegration, MCPConfig


class CalendarMCP(BaseMCPIntegration):
    """Calendar MCP integration supporting Google Calendar and Outlook."""

    name = "calendar"
    description = "Calendar integration for fetching events and availability"

    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.provider = config.provider or "google"
        self._client = None

    async def connect(self) -> bool:
        """Connect to calendar service."""
        try:
            if self.provider == "google":
                await self._connect_google()
            elif self.provider == "outlook":
                await self._connect_outlook()
            else:
                raise ValueError(f"Unsupported calendar provider: {self.provider}")

            self._connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to calendar: {e}")
            return False

    async def _connect_google(self) -> None:
        """Connect to Google Calendar."""
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds_path = self.config.credentials.get("credentials_path")
        if creds_path:
            with open(creds_path) as f:
                creds_data = json.load(f)
            creds = Credentials.from_authorized_user_info(creds_data)
            self._client = build("calendar", "v3", credentials=creds)

    async def _connect_outlook(self) -> None:
        """Connect to Outlook Calendar."""
        # Outlook connection implementation
        pass

    async def disconnect(self) -> None:
        """Disconnect from calendar service."""
        self._client = None
        self._connected = False

    async def health_check(self) -> Dict[str, Any]:
        """Check calendar connection health."""
        return {
            "connected": self._connected,
            "provider": self.provider,
            "status": "healthy" if self._connected else "disconnected"
        }

    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute calendar action."""
        actions = {
            "list_events": self.list_events,
            "get_event": self.get_event,
            "get_availability": self.get_availability,
            "create_event": self.create_event,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return await actions[action](**params)

    async def list_events(
        self,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """List calendar events."""
        if not self._connected or not self._client:
            return []

        try:
            if self.provider == "google":
                time_min = time_min or datetime.utcnow().isoformat() + "Z"
                time_max = time_max or (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

                events_result = self._client.events().list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime"
                ).execute()

                return events_result.get("items", [])
        except Exception as e:
            print(f"Error listing events: {e}")
            return []

    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific calendar event."""
        if not self._connected or not self._client:
            return None

        try:
            if self.provider == "google":
                return self._client.events().get(
                    calendarId="primary",
                    eventId=event_id
                ).execute()
        except Exception as e:
            print(f"Error getting event: {e}")
            return None

    async def get_availability(
        self,
        emails: List[str],
        time_min: str,
        time_max: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get availability for multiple users."""
        availability = {}

        if not self._connected or not self._client:
            return availability

        try:
            if self.provider == "google":
                body = {
                    "timeMin": time_min,
                    "timeMax": time_max,
                    "items": [{"id": email} for email in emails]
                }

                result = self._client.freebusy().query(body=body).execute()

                for email in emails:
                    calendar_data = result.get("calendars", {}).get(email, {})
                    availability[email] = calendar_data.get("busy", [])
        except Exception as e:
            print(f"Error getting availability: {e}")

        return availability

    async def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        attendees: List[str] = None,
        description: str = None,
        location: str = None
    ) -> Optional[Dict[str, Any]]:
        """Create a calendar event."""
        if not self._connected or not self._client:
            return None

        try:
            if self.provider == "google":
                event = {
                    "summary": summary,
                    "start": {"dateTime": start_time, "timeZone": "UTC"},
                    "end": {"dateTime": end_time, "timeZone": "UTC"},
                }

                if attendees:
                    event["attendees"] = [{"email": e} for e in attendees]
                if description:
                    event["description"] = description
                if location:
                    event["location"] = location

                return self._client.events().insert(
                    calendarId="primary",
                    body=event,
                    sendUpdates="all"
                ).execute()
        except Exception as e:
            print(f"Error creating event: {e}")
            return None

    def get_available_actions(self) -> List[str]:
        """Get available calendar actions."""
        return ["list_events", "get_event", "get_availability", "create_event"]
