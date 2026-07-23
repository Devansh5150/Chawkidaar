"""State persistence and crash recovery for Chawkidaar Loop Engine.

Handles snapshot serialization, atomic file disk storage, and state recovery.
"""

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from chawkidaar.loops.state_machine import LoopState


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class LoopStateSnapshot:
    """Serializable snapshot of LoopEngine state."""

    current_loop_number: int = 0
    current_state: str = LoopState.IDLE.value
    started_time: Optional[str] = None
    finished_time: Optional[str] = None
    last_checkpoint: Dict[str, Any] = field(default_factory=dict)
    active_project: str = "default"
    updated_at: str = field(default_factory=_utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoopStateSnapshot":
        """Create snapshot from dictionary."""
        return cls(
            current_loop_number=data.get("current_loop_number", 0),
            current_state=data.get("current_state", LoopState.IDLE.value),
            started_time=data.get("started_time"),
            finished_time=data.get("finished_time"),
            last_checkpoint=data.get("last_checkpoint", {}),
            active_project=data.get("active_project", "default"),
            updated_at=data.get("updated_at", _utc_now_iso()),
        )


class StatePersistence(ABC):
    """Abstract interface for state persistence."""

    @abstractmethod
    def save(self, snapshot: LoopStateSnapshot) -> None:
        """Save state snapshot."""
        pass

    @abstractmethod
    def load(self) -> Optional[LoopStateSnapshot]:
        """Load state snapshot if exists."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear persisted state."""
        pass


class FileStatePersistence(StatePersistence):
    """File-backed persistence store using atomic write operations."""

    def __init__(self, file_path: str | Path = ".chawkidaar/state.json"):
        self.file_path = Path(file_path)

    def save(self, snapshot: LoopStateSnapshot) -> None:
        """Atomically save snapshot to JSON file."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.file_path.with_suffix(".tmp")

        data = snapshot.to_dict()
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Atomic replace to prevent corrupted state files
        os.replace(tmp_path, self.file_path)

    def load(self) -> Optional[LoopStateSnapshot]:
        """Load snapshot from file if available. Return None if missing or corrupt."""
        if not self.file_path.exists():
            return None

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return LoopStateSnapshot.from_dict(data)
        except Exception as err:
            logging.getLogger("chawkidaar.persistence").warning(
                f"Failed to load state snapshot from {self.file_path}: {err}"
            )
            return None

    def clear(self) -> None:
        """Delete persisted state file if present."""
        if self.file_path.exists():
            try:
                self.file_path.unlink()
            except OSError:
                pass
