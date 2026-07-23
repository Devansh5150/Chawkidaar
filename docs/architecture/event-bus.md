# Event Bus Architecture

## Overview

The `EventBus` provides an in-memory publish-subscribe mechanism that decouples the `LoopEngine` from notification adapters (Telegram bot, CLI logging, dashboards, monitoring metrics).

## Core Event Types

- `LoopStarted`: Emitted when a loop cycle starts.
- `VerificationStarted`: Emitted when verification checks begin.
- `VerificationPassed`: Emitted when verification succeeds.
- `VerificationFailed`: Emitted when verification fails.
- `NotificationRequested`: Emitted when notification dispatch is required.
- `WaitingForApproval`: Emitted when human approval is required.
- `LoopApproved`: Emitted when a loop is approved.
- `LoopFailed`: Emitted when a loop fails.
- `LoopPaused`: Emitted when a loop is paused.
- `StateChanged`: Emitted on any state machine transition.

## Key Design Principles

1. **Subscriber Isolation**: Exceptions thrown in subscriber callbacks are caught and logged, preventing subscriber failures from crashing the engine loop.
2. **Zero Engine Coupling**: The `LoopEngine` publishes events without any knowledge of who is listening.
