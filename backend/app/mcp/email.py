"""Email MCP integration for Gmail and IMAP."""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import email
from email.header import decode_header

from app.mcp.base import BaseMCPIntegration, MCPConfig


class EmailMCP(BaseMCPIntegration):
    """Email MCP integration supporting Gmail and IMAP."""

    name = "email"
    description = "Email integration for searching and fetching messages"

    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.provider = config.provider or "imap"
        self._client = None

    async def connect(self) -> bool:
        """Connect to email service."""
        try:
            if self.provider == "gmail":
                await self._connect_gmail()
            elif self.provider == "imap":
                await self._connect_imap()
            else:
                raise ValueError(f"Unsupported email provider: {self.provider}")

            self._connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to email: {e}")
            return False

    async def _connect_gmail(self) -> None:
        """Connect to Gmail using OAuth."""
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        import json

        creds_path = self.config.credentials.get("credentials_path")
        if creds_path:
            with open(creds_path) as f:
                creds_data = json.load(f)
            creds = Credentials.from_authorized_user_info(creds_data)
            self._client = build("gmail", "v1", credentials=creds)

    async def _connect_imap(self) -> None:
        """Connect to IMAP server."""
        from imapclient import IMAPClient

        host = self.config.credentials.get("host")
        port = self.config.credentials.get("port", 993)
        username = self.config.credentials.get("username")
        password = self.config.credentials.get("password")

        self._client = IMAPClient(host, port=port, ssl=True)
        self._client.login(username, password)
        self._client.select_folder("INBOX")

    async def disconnect(self) -> None:
        """Disconnect from email service."""
        if self._client and self.provider == "imap":
            try:
                self._client.logout()
            except:
                pass
        self._client = None
        self._connected = False

    async def health_check(self) -> Dict[str, Any]:
        """Check email connection health."""
        return {
            "connected": self._connected,
            "provider": self.provider,
            "status": "healthy" if self._connected else "disconnected"
        }

    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute email action."""
        actions = {
            "search_emails": self.search_emails,
            "get_email": self.get_email,
            "get_thread": self.get_thread,
            "list_recent": self.list_recent,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return await actions[action](**params)

    async def search_emails(
        self,
        query: str,
        since: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """Search emails by query."""
        if not self._connected or not self._client:
            return []

        try:
            if self.provider == "gmail":
                results = self._client.users().messages().list(
                    userId="me",
                    q=query,
                    maxResults=max_results
                ).execute()

                messages = []
                for msg in results.get("messages", []):
                    full_msg = self._client.users().messages().get(
                        userId="me",
                        id=msg["id"],
                        format="full"
                    ).execute()
                    messages.append(self._parse_gmail_message(full_msg))

                return messages

            elif self.provider == "imap":
                criteria = ["ALL"]
                if since:
                    since_date = datetime.fromisoformat(since.replace("Z", "+00:00"))
                    criteria = ["SINCE", since_date.strftime("%d-%b-%Y")]

                message_ids = self._client.search(criteria)
                messages = []

                for uid in message_ids[-max_results:]:
                    raw = self._client.fetch([uid], ["RFC822"])
                    if uid in raw:
                        msg = email.message_from_bytes(raw[uid][b"RFC822"])
                        messages.append(self._parse_imap_message(msg, uid))

                return messages

        except Exception as e:
            print(f"Error searching emails: {e}")
            return []

    async def get_email(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific email by ID."""
        if not self._connected or not self._client:
            return None

        try:
            if self.provider == "gmail":
                msg = self._client.users().messages().get(
                    userId="me",
                    id=message_id,
                    format="full"
                ).execute()
                return self._parse_gmail_message(msg)

            elif self.provider == "imap":
                raw = self._client.fetch([int(message_id)], ["RFC822"])
                if int(message_id) in raw:
                    msg = email.message_from_bytes(raw[int(message_id)][b"RFC822"])
                    return self._parse_imap_message(msg, message_id)

        except Exception as e:
            print(f"Error getting email: {e}")
            return None

    async def get_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all emails in a thread."""
        if not self._connected or not self._client:
            return []

        try:
            if self.provider == "gmail":
                thread = self._client.users().threads().get(
                    userId="me",
                    id=thread_id,
                    format="full"
                ).execute()

                return [
                    self._parse_gmail_message(msg)
                    for msg in thread.get("messages", [])
                ]

        except Exception as e:
            print(f"Error getting thread: {e}")
            return []

    async def list_recent(
        self,
        days: int = 7,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """List recent emails."""
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        return await self.search_emails(query="", since=since, max_results=max_results)

    def _parse_gmail_message(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail API message."""
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

        body = ""
        payload = msg.get("payload", {})
        if "body" in payload and payload["body"].get("data"):
            import base64
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
        elif "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    import base64
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                    break

        return {
            "id": msg["id"],
            "thread_id": msg.get("threadId"),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "body": body[:2000],
            "snippet": msg.get("snippet", "")
        }

    def _parse_imap_message(self, msg: email.message.Message, uid: Any) -> Dict[str, Any]:
        """Parse IMAP message."""
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="ignore")

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        return {
            "id": str(uid),
            "from": msg["From"],
            "to": msg["To"],
            "subject": subject,
            "date": msg["Date"],
            "body": body[:2000]
        }

    def get_available_actions(self) -> List[str]:
        """Get available email actions."""
        return ["search_emails", "get_email", "get_thread", "list_recent"]
