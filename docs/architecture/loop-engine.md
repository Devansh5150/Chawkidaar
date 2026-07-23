# Loop Engine Architecture

## Overview

The `LoopEngine` is the core execution driver in Chawkidaar. It manages the iterative development, verification, notification, and approval cycle for autonomous AI agent loops.

## State Machine Integration

The loop engine encapsulates a 10-state Finite State Machine (`StateMachine`):

- `IDLE`: Initial idle state.
- `INITIALIZING`: Setting up loop context and loading persistent state.
- `RUNNING`: Executing agent task steps via `execute_step()`.
- `VERIFYING`: Executing test suites, code linters, and static analysis commands.
- `NOTIFYING`: Emitting event notifications to subscribers.
- `WAITING_FOR_APPROVAL`: Pending supervisor / human approval.
- `APPROVED`: Loop execution successfully completed.
- `PAUSED`: Execution temporarily suspended.
- `FAILED`: Task step failure or verification failure.
- `ROLLBACK`: Workspace rollback to last valid checkpoint.

## Primary Responsibilities

1. **Task Execution**: Safely invoking step functions with duration tracking and checkpointing.
2. **Event Emission**: Publishing lifecycle events to `EventBus` without coupling to subscribers.
3. **State Persistence**: Auto-syncing state snapshots to `StatePersistence` after every transition.
4. **Crash Recovery**: Restoring engine state upon application restart via `recover()`.
