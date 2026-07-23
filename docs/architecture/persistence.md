# Persistence & Crash Recovery Architecture

## Overview

The persistence layer (`FileStatePersistence`) preserves `LoopEngine` state snapshots across process restarts.

## Data Model

`LoopStateSnapshot` captures:
- `current_loop_number`: Active loop iteration number.
- `current_state`: String value of current `LoopState`.
- `started_time`: ISO UTC timestamp of loop start.
- `finished_time`: ISO UTC timestamp of loop completion.
- `last_checkpoint`: Checkpoint dictionary metadata.
- `active_project`: Project identifier string.
- `updated_at`: Last snapshot update timestamp.

## Atomic Storage Mechanic

To prevent file corruption during sudden system crashes or process kills:
1. Snapshot is serialized to JSON and written to a `.tmp` file.
2. An atomic file replace operation (`os.replace`) replaces the target file (`.chawkidaar/state.json`).
