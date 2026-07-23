"""Finite State Machine for Chawkidaar Loop Execution Engine.

Defines the core states, valid state transitions, and state machine exception handling.
"""

from enum import Enum
from typing import Any, Dict, Optional, Set


class LoopState(str, Enum):
    """Supported operational states for the Chawkidaar Loop Engine."""

    IDLE = "IDLE"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    NOTIFYING = "NOTIFYING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    APPROVED = "APPROVED"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    ROLLBACK = "ROLLBACK"


class InvalidStateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, from_state: LoopState, to_state: LoopState, reason: str = ""):
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason
        from_str = (
            from_state.value if isinstance(from_state, Enum) else str(from_state)
        )
        to_str = to_state.value if isinstance(to_state, Enum) else str(to_state)
        msg = f"Invalid state transition from '{from_str}' to '{to_str}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


# Explicit allowed transition graph
ALLOWED_TRANSITIONS: Dict[LoopState, Set[LoopState]] = {
    LoopState.IDLE: {
        LoopState.INITIALIZING,
    },
    LoopState.INITIALIZING: {
        LoopState.RUNNING,
        LoopState.FAILED,
    },
    LoopState.RUNNING: {
        LoopState.VERIFYING,
        LoopState.PAUSED,
        LoopState.FAILED,
    },
    LoopState.VERIFYING: {
        LoopState.NOTIFYING,
        LoopState.FAILED,
        LoopState.ROLLBACK,
    },
    LoopState.NOTIFYING: {
        LoopState.WAITING_FOR_APPROVAL,
        LoopState.APPROVED,
        LoopState.FAILED,
    },
    LoopState.WAITING_FOR_APPROVAL: {
        LoopState.APPROVED,
        LoopState.PAUSED,
        LoopState.FAILED,
        LoopState.ROLLBACK,
    },
    LoopState.APPROVED: {
        LoopState.IDLE,
        LoopState.INITIALIZING,
    },
    LoopState.PAUSED: {
        LoopState.RUNNING,
        LoopState.IDLE,
        LoopState.FAILED,
    },
    LoopState.FAILED: {
        LoopState.ROLLBACK,
        LoopState.INITIALIZING,
        LoopState.IDLE,
    },
    LoopState.ROLLBACK: {
        LoopState.IDLE,
        LoopState.FAILED,
    },
}


class StateMachine:
    """Manages loop state transitions and guarantees valid state progression."""

    def __init__(self, initial_state: LoopState = LoopState.IDLE):
        self._current_state: LoopState = initial_state
        self._history: list[Dict[str, Any]] = []

    @property
    def current_state(self) -> LoopState:
        """Return the current loop state."""
        return self._current_state

    @property
    def history(self) -> list[Dict[str, Any]]:
        """Return transition history."""
        return list(self._history)

    def can_transition_to(self, target_state: LoopState) -> bool:
        """Check if transitioning from current_state to target_state is allowed."""
        if not isinstance(target_state, LoopState):
            try:
                target_state = LoopState(target_state)
            except ValueError:
                return False

        allowed = ALLOWED_TRANSITIONS.get(self._current_state, set())
        return target_state in allowed

    def transition_to(
        self,
        target_state: LoopState,
        context: Optional[Dict[str, Any]] = None,
    ) -> LoopState:
        """Transition state machine to target_state if valid.

        Raises:
            InvalidStateTransitionError: If the transition is not allowed.
        """
        if not isinstance(target_state, LoopState):
            try:
                target_state = LoopState(target_state)
            except ValueError as err:
                raise InvalidStateTransitionError(
                    self._current_state,
                    target_state,
                    f"Unknown target state '{target_state}'",
                ) from err

        if not self.can_transition_to(target_state):
            reason = (
                f"Transition from {self._current_state.value} to "
                f"{target_state.value} is not permitted"
            )
            raise InvalidStateTransitionError(
                from_state=self._current_state,
                to_state=target_state,
                reason=reason,
            )

        from_state = self._current_state
        self._current_state = target_state
        self._history.append({
            "from_state": from_state.value,
            "to_state": target_state.value,
            "context": context or {},
        })
        return self._current_state

    def reset(self, state: LoopState = LoopState.IDLE) -> None:
        """Reset state machine directly to a state (used in recovery/force reset)."""
        self._current_state = state
