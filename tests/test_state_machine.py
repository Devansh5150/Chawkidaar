"""Unit tests for Finite State Machine."""

import pytest

from chawkidaar.loops.state_machine import (
    ALLOWED_TRANSITIONS,
    InvalidStateTransitionError,
    LoopState,
    StateMachine,
)


def test_initial_state():
    sm = StateMachine()
    assert sm.current_state == LoopState.IDLE
    assert len(sm.history) == 0


def test_all_valid_transitions():
    for source_state, valid_targets in ALLOWED_TRANSITIONS.items():
        for target_state in valid_targets:
            sm = StateMachine(initial_state=source_state)
            assert sm.can_transition_to(target_state) is True
            new_state = sm.transition_to(target_state)
            assert new_state == target_state
            assert sm.current_state == target_state
            assert len(sm.history) == 1
            assert sm.history[0]["from_state"] == source_state.value
            assert sm.history[0]["to_state"] == target_state.value


def test_invalid_transitions():
    all_states = set(LoopState)
    for source_state, valid_targets in ALLOWED_TRANSITIONS.items():
        invalid_targets = all_states - valid_targets
        for target_state in invalid_targets:
            sm = StateMachine(initial_state=source_state)
            assert sm.can_transition_to(target_state) is False
            with pytest.raises(InvalidStateTransitionError) as exc_info:
                sm.transition_to(target_state)
            assert exc_info.value.from_state == source_state
            assert exc_info.value.to_state == target_state


def test_string_transition_conversion():
    sm = StateMachine(initial_state=LoopState.IDLE)
    assert sm.transition_to("INITIALIZING") == LoopState.INITIALIZING
    assert sm.current_state == LoopState.INITIALIZING


def test_invalid_state_name_raises():
    sm = StateMachine(initial_state=LoopState.IDLE)
    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to("NON_EXISTENT_STATE")


def test_state_machine_reset():
    sm = StateMachine(initial_state=LoopState.IDLE)
    sm.transition_to(LoopState.INITIALIZING)
    assert sm.current_state == LoopState.INITIALIZING
    sm.reset(LoopState.IDLE)
    assert sm.current_state == LoopState.IDLE
