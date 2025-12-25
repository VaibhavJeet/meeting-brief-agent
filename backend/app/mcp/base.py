"""Base MCP integration class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class MCPConfig(BaseModel):
    """MCP integration configuration."""

    enabled: bool = False
    provider: Optional[str] = None
    credentials: Dict[str, Any] = {}
    options: Dict[str, Any] = {}


class BaseMCPIntegration(ABC):
    """Base class for MCP integrations."""

    name: str = "base"
    description: str = "Base MCP integration"

    def __init__(self, config: MCPConfig):
        self.config = config
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if integration is connected."""
        return self._connected

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the external service."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the external service."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the integration."""
        pass

    @abstractmethod
    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute an action on the external service."""
        pass

    def get_available_actions(self) -> List[str]:
        """Get list of available actions."""
        return []

    def validate_params(self, action: str, params: Dict[str, Any]) -> bool:
        """Validate parameters for an action."""
        return True
