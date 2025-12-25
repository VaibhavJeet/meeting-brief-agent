"""CRM MCP integration for HubSpot and Salesforce."""

from typing import Dict, Any, List, Optional
import httpx

from app.mcp.base import BaseMCPIntegration, MCPConfig


class CRMMCP(BaseMCPIntegration):
    """CRM MCP integration supporting HubSpot and Salesforce."""

    name = "crm"
    description = "CRM integration for contact and deal data"

    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.provider = config.provider or "hubspot"
        self._client = None
        self._api_key = config.credentials.get("api_key")

    async def connect(self) -> bool:
        """Connect to CRM service."""
        try:
            if self.provider == "hubspot":
                await self._connect_hubspot()
            elif self.provider == "salesforce":
                await self._connect_salesforce()
            else:
                raise ValueError(f"Unsupported CRM provider: {self.provider}")

            self._connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to CRM: {e}")
            return False

    async def _connect_hubspot(self) -> None:
        """Connect to HubSpot."""
        self._client = httpx.AsyncClient(
            base_url="https://api.hubapi.com",
            headers={"Authorization": f"Bearer {self._api_key}"}
        )
        # Verify connection
        response = await self._client.get("/crm/v3/objects/contacts?limit=1")
        response.raise_for_status()

    async def _connect_salesforce(self) -> None:
        """Connect to Salesforce."""
        # Salesforce OAuth implementation
        pass

    async def disconnect(self) -> None:
        """Disconnect from CRM service."""
        if self._client:
            await self._client.aclose()
        self._client = None
        self._connected = False

    async def health_check(self) -> Dict[str, Any]:
        """Check CRM connection health."""
        return {
            "connected": self._connected,
            "provider": self.provider,
            "status": "healthy" if self._connected else "disconnected"
        }

    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute CRM action."""
        actions = {
            "get_contact": self.get_contact,
            "get_contact_by_email": self.get_contact_by_email,
            "search_contacts": self.search_contacts,
            "get_contact_deals": self.get_contact_deals,
            "get_deal": self.get_deal,
            "get_account": self.get_account,
            "get_contact_activities": self.get_contact_activities,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return await actions[action](**params)

    async def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact by ID."""
        if not self._connected or not self._client:
            return None

        try:
            if self.provider == "hubspot":
                response = await self._client.get(
                    f"/crm/v3/objects/contacts/{contact_id}",
                    params={"properties": "firstname,lastname,email,company,jobtitle,phone"}
                )
                response.raise_for_status()
                data = response.json()
                return self._parse_hubspot_contact(data)
        except Exception as e:
            print(f"Error getting contact: {e}")
            return None

    async def get_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get contact by email address."""
        if not self._connected or not self._client:
            return None

        try:
            if self.provider == "hubspot":
                response = await self._client.post(
                    "/crm/v3/objects/contacts/search",
                    json={
                        "filterGroups": [{
                            "filters": [{
                                "propertyName": "email",
                                "operator": "EQ",
                                "value": email
                            }]
                        }],
                        "properties": ["firstname", "lastname", "email", "company", "jobtitle", "phone"]
                    }
                )
                response.raise_for_status()
                data = response.json()
                if data.get("results"):
                    return self._parse_hubspot_contact(data["results"][0])
        except Exception as e:
            print(f"Error getting contact by email: {e}")
        return None

    async def search_contacts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search contacts."""
        if not self._connected or not self._client:
            return []

        try:
            if self.provider == "hubspot":
                response = await self._client.post(
                    "/crm/v3/objects/contacts/search",
                    json={
                        "query": query,
                        "limit": limit,
                        "properties": ["firstname", "lastname", "email", "company", "jobtitle"]
                    }
                )
                response.raise_for_status()
                data = response.json()
                return [self._parse_hubspot_contact(c) for c in data.get("results", [])]
        except Exception as e:
            print(f"Error searching contacts: {e}")
        return []

    async def get_contact_deals(self, contact_id: str) -> List[Dict[str, Any]]:
        """Get deals associated with a contact."""
        if not self._connected or not self._client:
            return []

        try:
            if self.provider == "hubspot":
                response = await self._client.get(
                    f"/crm/v3/objects/contacts/{contact_id}/associations/deals"
                )
                response.raise_for_status()
                associations = response.json()

                deals = []
                for assoc in associations.get("results", []):
                    deal = await self.get_deal(assoc["id"])
                    if deal:
                        deals.append(deal)
                return deals
        except Exception as e:
            print(f"Error getting contact deals: {e}")
        return []

    async def get_deal(self, deal_id: str) -> Optional[Dict[str, Any]]:
        """Get deal by ID."""
        if not self._connected or not self._client:
            return None

        try:
            if self.provider == "hubspot":
                response = await self._client.get(
                    f"/crm/v3/objects/deals/{deal_id}",
                    params={"properties": "dealname,amount,dealstage,closedate,pipeline"}
                )
                response.raise_for_status()
                data = response.json()
                return self._parse_hubspot_deal(data)
        except Exception as e:
            print(f"Error getting deal: {e}")
        return None

    async def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get company/account by ID."""
        if not self._connected or not self._client:
            return None

        try:
            if self.provider == "hubspot":
                response = await self._client.get(
                    f"/crm/v3/objects/companies/{account_id}",
                    params={"properties": "name,domain,industry,numberofemployees,annualrevenue"}
                )
                response.raise_for_status()
                data = response.json()
                return self._parse_hubspot_company(data)
        except Exception as e:
            print(f"Error getting account: {e}")
        return None

    async def get_contact_activities(
        self,
        contact_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get recent activities for a contact."""
        if not self._connected or not self._client:
            return []

        try:
            if self.provider == "hubspot":
                # Get notes, calls, emails, meetings
                activities = []
                for obj_type in ["notes", "calls", "emails", "meetings"]:
                    response = await self._client.get(
                        f"/crm/v3/objects/contacts/{contact_id}/associations/{obj_type}"
                    )
                    if response.status_code == 200:
                        for assoc in response.json().get("results", [])[:5]:
                            activities.append({
                                "type": obj_type,
                                "id": assoc["id"]
                            })
                return activities[:limit]
        except Exception as e:
            print(f"Error getting activities: {e}")
        return []

    def _parse_hubspot_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse HubSpot contact data."""
        props = data.get("properties", {})
        return {
            "id": data.get("id"),
            "email": props.get("email"),
            "name": f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
            "company": props.get("company"),
            "title": props.get("jobtitle"),
            "phone": props.get("phone"),
            "crm_provider": "hubspot"
        }

    def _parse_hubspot_deal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse HubSpot deal data."""
        props = data.get("properties", {})
        return {
            "id": data.get("id"),
            "name": props.get("dealname"),
            "value": props.get("amount"),
            "stage": props.get("dealstage"),
            "close_date": props.get("closedate"),
            "pipeline": props.get("pipeline")
        }

    def _parse_hubspot_company(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse HubSpot company data."""
        props = data.get("properties", {})
        return {
            "id": data.get("id"),
            "name": props.get("name"),
            "domain": props.get("domain"),
            "industry": props.get("industry"),
            "employees": props.get("numberofemployees"),
            "revenue": props.get("annualrevenue")
        }

    def get_available_actions(self) -> List[str]:
        """Get available CRM actions."""
        return [
            "get_contact", "get_contact_by_email", "search_contacts",
            "get_contact_deals", "get_deal", "get_account", "get_contact_activities"
        ]
