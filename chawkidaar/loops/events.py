"""Internal Event System and Event Bus for Chawkidaar Loop Engine.

Allows decoupled event emission and subscription across modules.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
import uuid


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class LoopEvent:
    """Base event structure for all loop lifecycle events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = field(default="LoopEvent")
    timestamp: str = field(default_factory=_utc_now_iso)
    loop_number: int = field(default=0)
    project_name: str = field(default="")
    payload: dict = field(default_factory=dict)


@dataclass
class LoopStarted(LoopEvent):
    """Emitted when a loop execution starts."""

    event_type: str = "LoopStarted"


@dataclass
class VerificationStarted(LoopEvent):
    """Emitted when task verification begins."""

    event_type: str = "VerificationStarted"


@dataclass
class VerificationPassed(LoopEvent):
    """Emitted when task verification succeeds."""

    event_type: str = "VerificationPassed"


@dataclass
class VerificationFailed(LoopEvent):
    """Emitted when task verification fails."""

    event_type: str = "VerificationFailed"


@dataclass
class NotificationRequested(LoopEvent):
    """Emitted when notification dispatch is requested."""

    event_type: str = "NotificationRequested"


@dataclass
class WaitingForApproval(LoopEvent):
    """Emitted when loop enters WAITING_FOR_APPROVAL state."""

    event_type: str = "WaitingForApproval"


@dataclass
class LoopApproved(LoopEvent):
    """Emitted when a loop is approved."""

    event_type: str = "LoopApproved"


@dataclass
class LoopFailed(LoopEvent):
    """Emitted when a loop fails."""

    event_type: str = "LoopFailed"


@dataclass
class LoopPaused(LoopEvent):
    """Emitted when a loop is paused."""

    event_type: str = "LoopPaused"


@dataclass
class StateChanged(LoopEvent):
    """Emitted on any state transition."""

    event_type: str = "StateChanged"
    from_state: str = field(default="")
    to_state: str = field(default="")


class EventBus:
    """In-memory event bus supporting publish-subscribe pattern."""

    def __init__(self):
        self._subscribers: dict[str, list] = {}
        self._global_subscribers: list = []

    def subscribe(self, event_type: str | None, callback) -> None:
        """Subscribe callback to event_type (or all events if event_type is None)."""
        if event_type is None:
            if callback not in self._global_subscribers:
                self._global_subscribers.append(callback)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str | None, callback) -> None:
        """Unsubscribe callback from event type or global subscriber list."""
        if event_type is None:
            if callback in self._global_subscribers:
                self._global_subscribers.remove(callback)
        else:
            subs = self._subscribers.get(event_type, [])
            if callback in subs:
                subs.remove(callback)

    def publish(self, event: LoopEvent) -> None:
        """Publish event to all matched subscribers.

        Exceptions in subscribers are caught to ensure engine isolation.
        """
        callbacks = list(self._global_subscribers)
        if event.event_type in self._subscribers:
            callbacks.extend(self._subscribers[event.event_type])

        for cb in callbacks:
            try:
                cb(event)
            except Exception as e:
                logging.getLogger("chawkidaar.event_bus").error(
                    f"Error in subscriber callback {cb}: {e}", exc_info=True
                )

    def clear(self) -> None:
        """Clear all subscribers."""
        self._subscribers.clear()
        self._global_subscribers.clear()
