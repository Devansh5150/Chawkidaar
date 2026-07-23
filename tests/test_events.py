"""Unit tests for Event Bus and Loop Events."""

from chawkidaar.loops.events import (
    EventBus,
    LoopApproved,
    LoopFailed,
    LoopStarted,
    StateChanged,
    VerificationStarted,
)


def test_event_instantiation():
    event = LoopStarted(loop_number=1, project_name="test_proj", payload={"key": "val"})
    assert event.event_type == "LoopStarted"
    assert event.loop_number == 1
    assert event.project_name == "test_proj"
    assert event.payload == {"key": "val"}
    assert event.event_id is not None
    assert event.timestamp is not None


def test_event_bus_specific_subscription():
    bus = EventBus()
    received = []

    def on_started(ev):
        received.append(ev)

    bus.subscribe("LoopStarted", on_started)

    ev1 = LoopStarted(loop_number=1)
    ev2 = LoopFailed(loop_number=1)

    bus.publish(ev1)
    bus.publish(ev2)

    assert len(received) == 1
    assert received[0] == ev1


def test_event_bus_global_subscription():
    bus = EventBus()
    received = []

    def on_any(ev):
        received.append(ev)

    bus.subscribe(None, on_any)

    ev1 = LoopStarted(loop_number=1)
    ev2 = VerificationStarted(loop_number=1)

    bus.publish(ev1)
    bus.publish(ev2)

    assert len(received) == 2
    assert received[0] == ev1
    assert received[1] == ev2


def test_event_bus_unsubscribe():
    bus = EventBus()
    received = []

    def on_approved(ev):
        received.append(ev)

    bus.subscribe("LoopApproved", on_approved)
    ev = LoopApproved(loop_number=1)

    bus.publish(ev)
    assert len(received) == 1

    bus.unsubscribe("LoopApproved", on_approved)
    bus.publish(ev)
    assert len(received) == 1


def test_subscriber_exception_isolation():
    bus = EventBus()
    calls = []

    def faulty_subscriber(ev):
        raise RuntimeError("Subscriber crash!")

    def good_subscriber(ev):
        calls.append(ev)

    bus.subscribe(None, faulty_subscriber)
    bus.subscribe(None, good_subscriber)

    ev = StateChanged(loop_number=1, from_state="IDLE", to_state="INITIALIZING")
    # Should not raise exception
    bus.publish(ev)

    assert len(calls) == 1
    assert calls[0] == ev
