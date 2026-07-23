# Chawkidaar 🛡️

An autonomous AI agent monitoring, loop engineering, and alerting system.

## Project Structure

```
Chawkidaar/
│
├── chawkidaar/
│   ├── __init__.py
│   ├── main.py
│   ├── cli/
│   ├── telegram/
│   ├── agents/
│   ├── loops/
│   │   ├── state_machine.py    # Finite State Machine & transitions
│   │   ├── events.py           # Decoupled Event Bus & Loop events
│   │   ├── persistence.py      # Atomic state persistence & crash recovery
│   │   ├── engine.py           # Core Loop Execution Engine
│   │   └── __init__.py
│   ├── config/
│   └── utils/
│       ├── logger.py           # Structured JSON / Console Logging
│       └── __init__.py
│
├── tests/                      # Unit tests (100% pass rate)
├── docs/                       # Architecture & design documentation
├── configs/
├── README.md
├── pyproject.toml
└── .gitignore
```

## Features

- **Core Loop Engine (Loop #002)**: Reusable, decoupled loop execution engine supporting state transition validation, checkpointing, event emission, duration recording, and crash recovery.
- **Finite State Machine**: 10 distinct states (`IDLE`, `INITIALIZING`, `RUNNING`, `VERIFYING`, `NOTIFYING`, `WAITING_FOR_APPROVAL`, `APPROVED`, `PAUSED`, `FAILED`, `ROLLBACK`) with enforced valid transitions.
- **Event System**: In-memory `EventBus` allowing subscribers (Telegram, logging, metrics) to subscribe to lifecycle events without coupling to the loop engine.
- **Crash Recovery**: Atomic file persistence (`.chawkidaar/state.json`) guaranteeing corruption-free snapshot recovery upon restart.

## Documentation

- [Core Loop Engine & Architecture Document](docs/core_loop_engine.md)

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Devansh5150/Chawkidaar.git
cd Chawkidaar

# Activate virtual environment
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On Linux/macOS

# Install dependencies in editable mode
pip install -e .
```

### Running Tests

```bash
pytest -v
```

## License

[MIT](LICENSE)