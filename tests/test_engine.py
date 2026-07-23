"""Unit tests for Loop Engine integration and lifecycle."""

from pathlib import Path

from chawkidaar.loops.engine import LoopEngine
from chawkidaar.loops.events import EventBus
from chawkidaar.loops.persistence import FileStatePersistence
from chawkidaar.loops.state_machine import LoopState


def test_loop_engine_full_successful_flow(tmp_path: Path):
    persistence = FileStatePersistence(file_path=tmp_path / "state.json")
    event_bus = EventBus()
    emitted_events = []

    event_bus.subscribe(None, lambda ev: emitted_events.append(ev.event_type))

    engine = LoopEngine(
        active_project="test_app",
        persistence=persistence,
        event_bus=event_bus,
        auto_recover=False,
    )

    assert engine.current_state == LoopState.IDLE
    assert engine.current_loop_number == 0

    # Start loop
    engine.start_loop(payload={"task": "feature_x"})
    assert engine.current_state == LoopState.RUNNING
    assert engine.current_loop_number == 1
    assert engine.started_time is not None
    assert engine.duration_seconds >= 0.0

    # Execute task step
    def dummy_task():
        return "success"

    res = engine.execute_step("build", dummy_task)
    assert res == "success"
    assert "step_build_success" in engine.last_checkpoint["checkpoint_name"]

    # Verify
    verified = engine.verify(lambda: True)
    assert verified is True
    assert engine.current_state == LoopState.NOTIFYING

    # Request approval
    engine.request_approval()
    assert engine.current_state == LoopState.WAITING_FOR_APPROVAL

    # Approve
    engine.approve()
    assert engine.current_state == LoopState.APPROVED
    assert engine.finished_time is not None

    # Check emitted lifecycle events
    expected = [
        "StateChanged",         # IDLE -> INITIALIZING
        "StateChanged",         # INITIALIZING -> RUNNING
        "LoopStarted",
        "StateChanged",         # RUNNING -> VERIFYING
        "VerificationStarted",
        "VerificationPassed",
        "StateChanged",         # VERIFYING -> NOTIFYING
        "NotificationRequested",
        "StateChanged",         # NOTIFYING -> WAITING_FOR_APPROVAL
        "WaitingForApproval",
        "StateChanged",         # WAITING_FOR_APPROVAL -> APPROVED
        "LoopApproved",
    ]
    assert emitted_events == expected


def test_loop_engine_verification_failure_and_rollback(tmp_path: Path):
    persistence = FileStatePersistence(file_path=tmp_path / "state.json")
    event_bus = EventBus()
    emitted_events = []
    event_bus.subscribe(None, lambda ev: emitted_events.append(ev.event_type))

    engine = LoopEngine(
        active_project="rollback_test",
        persistence=persistence,
        event_bus=event_bus,
        auto_recover=False,
    )

    engine.start_loop()
    verified = engine.verify(lambda: False)
    assert verified is False
    assert engine.current_state == LoopState.ROLLBACK

    assert "VerificationFailed" in emitted_events


def test_loop_engine_pause_and_resume(tmp_path: Path):
    persistence = FileStatePersistence(file_path=tmp_path / "state.json")
    engine = LoopEngine(
        active_project="pause_test",
        persistence=persistence,
        auto_recover=False,
    )

    engine.start_loop()
    assert engine.current_state == LoopState.RUNNING

    engine.pause()
    assert engine.current_state == LoopState.PAUSED

    engine.resume()
    assert engine.current_state == LoopState.RUNNING


def test_loop_engine_failure_and_recovery(tmp_path: Path):
    state_file = tmp_path / "crash_recovery_state.json"
    persistence = FileStatePersistence(file_path=state_file)

    # Engine instance 1: Starts loop and runs task
    engine1 = LoopEngine(
        active_project="recover_proj",
        persistence=persistence,
        auto_recover=False,
    )
    engine1.start_loop(payload={"ref": "v1.0"})
    engine1.record_checkpoint("custom_checkpoint", {"file": "main.py"})

    assert state_file.exists()

    # Simulate crash and restart: Engine instance 2 loads state
    engine2 = LoopEngine(
        active_project="recover_proj",
        persistence=persistence,
        auto_recover=True,
    )

    assert engine2.current_state == LoopState.RUNNING
    assert engine2.current_loop_number == 1
    assert engine2.active_project == "recover_proj"
    assert engine2.last_checkpoint["data"] == {"file": "main.py"}
