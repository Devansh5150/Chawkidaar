"""Core Loop Engine for Chawkidaar.

Coordinates state transitions, task execution, duration tracking, event publishing,
and persistence recovery. Completely independent of Telegram or UI layers.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from chawkidaar.loops.events import (
    EventBus,
    LoopApproved,
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
from chawkidaar.loops.state_machine import LoopState, StateMachine

logger = logging.getLogger("chawkidaar.loop_engine")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


class LoopEngine:
    """Core autonomous loop execution engine for managing agent loops."""

    def __init__(
        self,
        active_project: str = "default",
        persistence: Optional[StatePersistence] = None,
        event_bus: Optional[EventBus] = None,
        auto_recover: bool = True,
    ):
        self.active_project = active_project
        self.persistence = persistence or FileStatePersistence()
        self.event_bus = event_bus or EventBus()
        self.state_machine = StateMachine(LoopState.IDLE)

        self.current_loop_number: int = 0
        self.started_time: Optional[datetime] = None
        self.finished_time: Optional[datetime] = None
        self.last_checkpoint: Dict[str, Any] = {}

        if auto_recover:
            self.recover()

    @property
    def current_state(self) -> LoopState:
        """Get current loop state."""
        return self.state_machine.current_state

    @property
    def duration_seconds(self) -> float:
        """Calculate active duration in seconds."""
        if not self.started_time:
            return 0.0
        end = self.finished_time or _utc_now()
        return (end - self.started_time).total_seconds()

    def _create_snapshot(self) -> LoopStateSnapshot:
        """Build current state snapshot."""
        started_iso = self.started_time.isoformat() if self.started_time else None
        finished_iso = (
            self.finished_time.isoformat() if self.finished_time else None
        )
        return LoopStateSnapshot(
            current_loop_number=self.current_loop_number,
            current_state=self.current_state.value,
            started_time=started_iso,
            finished_time=finished_iso,
            last_checkpoint=self.last_checkpoint,
            active_project=self.active_project,
            updated_at=_utc_now_iso(),
        )

    def _sync_persistence(self) -> None:
        """Save current snapshot to persistence store."""
        try:
            self.persistence.save(self._create_snapshot())
        except Exception as e:
            logger.error(f"Failed to sync state to persistence: {e}", exc_info=True)

    def transition_to(
        self,
        target_state: LoopState,
        payload: Optional[Dict[str, Any]] = None,
    ) -> LoopState:
        """Transition loop engine to target_state, sync state, and publish events."""
        from_state = self.current_state
        new_state = self.state_machine.transition_to(target_state, context=payload)

        self._sync_persistence()

        # Emit StateChanged event
        self.event_bus.publish(
            StateChanged(
                loop_number=self.current_loop_number,
                project_name=self.active_project,
                from_state=from_state.value,
                to_state=new_state.value,
                payload=payload or {},
            )
        )

        return new_state

    def start_loop(self, payload: Optional[Dict[str, Any]] = None) -> None:
        """Start a new loop cycle."""
        if self.current_state in (LoopState.APPROVED, LoopState.IDLE):
            self.transition_to(LoopState.INITIALIZING, payload=payload)
        elif self.current_state != LoopState.INITIALIZING:
            # Transitioning will raise InvalidStateTransitionError if invalid
            self.transition_to(LoopState.INITIALIZING, payload=payload)

        self.current_loop_number += 1
        self.started_time = _utc_now()
        self.finished_time = None
        self.last_checkpoint = {
            "checkpoint_name": "loop_init",
            "timestamp": _utc_now_iso(),
            "loop_number": self.current_loop_number,
        }

        # Transition to RUNNING
        self.transition_to(LoopState.RUNNING, payload=payload)

        # Emit LoopStarted event
        self.event_bus.publish(
            LoopStarted(
                loop_number=self.current_loop_number,
                project_name=self.active_project,
                payload=payload or {},
            )
        )

    def execute_step(
        self,
        step_name: str,
        step_fn: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Any:
        """Execute a step function within RUNNING state."""
        if self.current_state != LoopState.RUNNING:
            msg = (
                f"Cannot execute step '{step_name}' when loop engine is in state "
                f"'{self.current_state.value}'"
            )
            raise RuntimeError(msg)

        logger.info(
            f"Executing step '{step_name}' for loop #{self.current_loop_number}"
        )
        try:
            result = step_fn(*args, **kwargs)
            self.record_checkpoint(
                checkpoint_name=f"step_{step_name}_success",
                data={"result_summary": str(result)[:200]},
            )
            return result
        except Exception as err:
            logger.error(f"Step '{step_name}' failed: {err}", exc_info=True)
            self.fail(reason=f"Step '{step_name}' error: {err}")
            raise

    def record_checkpoint(self, checkpoint_name: str, data: Dict[str, Any]) -> None:
        """Record checkpoint metadata."""
        self.last_checkpoint = {
            "checkpoint_name": checkpoint_name,
            "timestamp": _utc_now_iso(),
            "loop_number": self.current_loop_number,
            "data": data,
        }
        self._sync_persistence()

    def verify(self, verifier_fn: Optional[Callable[[], bool]] = None) -> bool:
        """Verify the loop execution results."""
        self.transition_to(LoopState.VERIFYING)
        self.event_bus.publish(
            VerificationStarted(
                loop_number=self.current_loop_number,
                project_name=self.active_project,
            )
        )

        passed = True
        if verifier_fn:
            try:
                passed = verifier_fn()
            except Exception as e:
                logger.error(f"Verification function error: {e}", exc_info=True)
                passed = False

        if passed:
            self.event_bus.publish(
                VerificationPassed(
                    loop_number=self.current_loop_number,
                    project_name=self.active_project,
                )
            )
            self.transition_to(LoopState.NOTIFYING)
            self.event_bus.publish(
                NotificationRequested(
                    loop_number=self.current_loop_number,
                    project_name=self.active_project,
                )
            )
            return True
        else:
            self.event_bus.publish(
                VerificationFailed(
                    loop_number=self.current_loop_number,
                    project_name=self.active_project,
                )
            )
            self.transition_to(LoopState.ROLLBACK)
            return False

    def request_approval(self) -> None:
        """Request human or supervisor approval."""
        if self.current_state != LoopState.NOTIFYING:
            msg = f"Cannot request approval from state '{self.current_state.value}'"
            raise RuntimeError(msg)
        self.transition_to(LoopState.WAITING_FOR_APPROVAL)
        self.event_bus.publish(
            WaitingForApproval(
                loop_number=self.current_loop_number,
                project_name=self.active_project,
            )
        )

    def approve(self) -> None:
        """Approve the current loop."""
        if self.current_state in (LoopState.NOTIFYING, LoopState.WAITING_FOR_APPROVAL):
            self.transition_to(LoopState.APPROVED)
            self.finished_time = _utc_now()
            self._sync_persistence()
            self.event_bus.publish(
                LoopApproved(
                    loop_number=self.current_loop_number,
                    project_name=self.active_project,
                    payload={"duration_seconds": self.duration_seconds},
                )
            )

    def pause(self) -> None:
        """Pause running or waiting loop."""
        self.transition_to(LoopState.PAUSED)
        self.event_bus.publish(
            LoopPaused(
                loop_number=self.current_loop_number,
                project_name=self.active_project,
            )
        )

    def resume(self) -> None:
        """Resume paused loop back to RUNNING."""
        self.transition_to(LoopState.RUNNING)

    def fail(self, reason: str = "") -> None:
        """Mark loop as failed."""
        self.finished_time = _utc_now()
        self.transition_to(LoopState.FAILED, payload={"reason": reason})
        self.event_bus.publish(
            LoopFailed(
                loop_number=self.current_loop_number,
                project_name=self.active_project,
                payload={"reason": reason, "duration_seconds": self.duration_seconds},
            )
        )

    def rollback(self, checkpoint_id: Optional[str] = None) -> None:
        """Trigger rollback procedure."""
        self.transition_to(
            LoopState.ROLLBACK, payload={"checkpoint_id": checkpoint_id}
        )

    def recover(self) -> bool:
        """Recover engine state from persistent store."""
        snapshot = self.persistence.load()
        if not snapshot:
            logger.info("No persistent state found. Initialized fresh IDLE engine.")
            return False

        logger.info(
            f"Recovering state: loop #{snapshot.current_loop_number}, "
            f"state={snapshot.current_state}"
        )
        self.current_loop_number = snapshot.current_loop_number
        self.active_project = snapshot.active_project
        self.last_checkpoint = snapshot.last_checkpoint
        self.started_time = (
            datetime.fromisoformat(snapshot.started_time)
            if snapshot.started_time
            else None
        )
        self.finished_time = (
            datetime.fromisoformat(snapshot.finished_time)
            if snapshot.finished_time
            else None
        )

        recovered_state = LoopState(snapshot.current_state)
        self.state_machine.reset(recovered_state)
        return True
