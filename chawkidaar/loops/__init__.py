"""Core Loop Engine module for Chawkidaar."""

from chawkidaar.loops.engine import LoopEngine
from chawkidaar.loops.events import (
    EventBus,
    LoopApproved,
    LoopEvent,
    LoopFailed,
    LoopPaused,
    LoopStarted,
    NotificationRequested,
    StateChanged,
    VerificationFailed,
    VerificationPassed,
    VerificationStarted,
    WaitingForApproval,
)
from chawkidaar.loops.persistence import (
    FileStatePersistence,
    LoopStateSnapshot,
    StatePersistence,
)
from chawkidaar.loops.state_machine import (
    ALLOWED_TRANSITIONS,
    InvalidStateTransitionError,
    LoopState,
    StateMachine,
)

__all__ = [
    "LoopState",
    "StateMachine",
    "InvalidStateTransitionError",
    "ALLOWED_TRANSITIONS",
    "LoopEvent",
    "LoopStarted",
    "VerificationStarted",
    "VerificationPassed",
    "VerificationFailed",
    "NotificationRequested",
    "WaitingForApproval",
    "LoopApproved",
    "LoopFailed",
    "LoopPaused",
    "StateChanged",
    "EventBus",
    "LoopStateSnapshot",
    "StatePersistence",
    "FileStatePersistence",
    "LoopEngine",
]
