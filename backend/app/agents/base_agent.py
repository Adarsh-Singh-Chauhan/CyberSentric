"""
CyberSentric Base Agent
Abstract base class for all AI agents in the system.
"""
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    NONE = "none"


class AgentStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ALERT = "alert"
    ERROR = "error"


class ThreatResult(BaseModel):
    """Standardized threat detection result."""
    threat_detected: bool = False
    threat_type: str = "none"
    severity: Severity = Severity.NONE
    confidence: float = 0.0
    description: str = ""
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    raw_input: Optional[str] = None
    sanitized_input: Optional[str] = None
    recommended_actions: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class AgentEvent(BaseModel):
    """Event emitted by an agent."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_name: str
    event_type: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    data: dict = Field(default_factory=dict)
    severity: Severity = Severity.NONE


class ActionResult(BaseModel):
    """Result of an automated response action."""
    action_type: str
    success: bool
    target: str = ""
    description: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict = Field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base agent. All CyberSentric agents inherit from this."""

    def __init__(self, name: str):
        self.name = name
        self.status = AgentStatus.IDLE
        self.events: list[AgentEvent] = []
        self.processed_count = 0
        self.threats_detected = 0
        self.last_active = datetime.utcnow().isoformat()

    @abstractmethod
    async def process(self, data: dict) -> Any:
        """Process input data. Must be implemented by each agent."""
        pass

    def emit_event(self, event_type: str, data: dict, severity: Severity = Severity.NONE) -> AgentEvent:
        """Create and store an agent event."""
        event = AgentEvent(
            agent_name=self.name,
            event_type=event_type,
            data=data,
            severity=severity,
        )
        self.events.append(event)
        # Keep only last 100 events in memory
        if len(self.events) > 100:
            self.events = self.events[-100:]
        self.last_active = datetime.utcnow().isoformat()
        return event

    def get_status(self) -> dict:
        """Get current agent status."""
        return {
            "name": self.name,
            "status": self.status.value,
            "processed_count": self.processed_count,
            "threats_detected": self.threats_detected,
            "last_active": self.last_active,
            "recent_events": len(self.events),
        }
