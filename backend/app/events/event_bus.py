"""
Event Bus System
Phase 7.2: Event-driven architecture for VAJRA Core
"""
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime
from enum import Enum
import json
import asyncio
from dataclasses import dataclass, asdict


class EventType(str, Enum):
    """Event type definitions"""
    # Configuration events
    CONFIG_UPLOADED = "config.uploaded"
    CONFIG_UPDATED = "config.updated"
    CONFIG_DELETED = "config.deleted"
    CONFIG_VERSION_CREATED = "config.version.created"
    
    # Audit events
    AUDIT_STARTED = "audit.started"
    AUDIT_COMPLETED = "audit.completed"
    AUDIT_FAILED = "audit.failed"
    
    # Finding events
    FINDING_CREATED = "finding.created"
    FINDING_CRITICAL = "finding.critical"
    FINDING_HIGH = "finding.high"
    FINDING_RESOLVED = "finding.resolved"
    
    # Drift events
    DRIFT_DETECTED = "drift.detected"
    DRIFT_CRITICAL = "drift.critical"
    DRIFT_ACKNOWLEDGED = "drift.acknowledged"
    
    # Device events
    DEVICE_ADDED = "device.added"
    DEVICE_UPDATED = "device.updated"
    DEVICE_REMOVED = "device.removed"
    DEVICE_STATUS_CHANGED = "device.status.changed"
    
    # Posture events
    POSTURE_DEGRADED = "posture.degraded"
    POSTURE_IMPROVED = "posture.improved"
    POSTURE_CRITICAL = "posture.critical"
    
    # Remediation events
    REMEDIATION_CREATED = "remediation.created"
    REMEDIATION_APPROVED = "remediation.approved"
    REMEDIATION_REJECTED = "remediation.rejected"
    REMEDIATION_APPLIED = "remediation.applied"
    
    # User events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATED = "user.created"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


@dataclass
class Event:
    """Event data structure"""
    event_id: str
    event_type: EventType
    timestamp: str
    organization_id: int
    user_id: Optional[int]
    resource_type: str
    resource_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class EventBus:
    """
    Central event bus for application-wide event handling
    
    Supports:
    - Event subscription/publishing
    - Async event handlers
    - Event history
    - Webhook integration
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
        
    def subscribe(self, event_type: EventType, handler: Callable):
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async function to handle the event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """Unsubscribe from an event type"""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
    
    async def publish(self, event: Event):
        """
        Publish an event to all subscribers
        
        Args:
            event: Event to publish
        """
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Get handlers for this event type
        handlers = self._handlers.get(event.event_type, [])
        
        # Execute all handlers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
                # Don't let one handler failure affect others
    
    def get_history(
        self,
        event_type: Optional[EventType] = None,
        organization_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Event]:
        """
        Get event history with optional filtering
        """
        history = self._event_history
        
        if event_type:
            history = [e for e in history if e.event_type == event_type]
        
        if organization_id:
            history = [e for e in history if e.organization_id == organization_id]
        
        return list(reversed(history[-limit:]))


# Global event bus instance
event_bus = EventBus()


def create_event(
    event_type: EventType,
    organization_id: int,
    resource_type: str,
    resource_id: str,
    data: Dict[str, Any],
    user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Event:
    """
    Create a new event
    
    Args:
        event_type: Type of event
        organization_id: Organization ID
        resource_type: Type of resource (device, config, audit, etc.)
        resource_id: ID of the resource
        data: Event-specific data
        user_id: User who triggered the event (optional)
        metadata: Additional metadata (optional)
    
    Returns:
        Event object
    """
    import uuid
    
    return Event(
        event_id=f"EVT-{uuid.uuid4().hex[:12].upper()}",
        event_type=event_type,
        timestamp=datetime.utcnow().isoformat(),
        organization_id=organization_id,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        data=data,
        metadata=metadata or {}
    )


async def publish_event(
    event_type: EventType,
    organization_id: int,
    resource_type: str,
    resource_id: str,
    data: Dict[str, Any],
    user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Helper function to create and publish an event
    """
    event = create_event(
        event_type=event_type,
        organization_id=organization_id,
        resource_type=resource_type,
        resource_id=resource_id,
        data=data,
        user_id=user_id,
        metadata=metadata
    )
    
    await event_bus.publish(event)
    
    return event
