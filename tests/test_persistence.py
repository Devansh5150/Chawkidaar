"""Unit tests for State Persistence."""

from pathlib import Path

from chawkidaar.loops.persistence import FileStatePersistence, LoopStateSnapshot
from chawkidaar.loops.state_machine import LoopState


def test_snapshot_to_from_dict():
    snap = LoopStateSnapshot(
        current_loop_number=42,
        current_state=LoopState.RUNNING.value,
        started_time="2026-07-23T12:00:00Z",
        finished_time=None,
        last_checkpoint={"step": "compile"},
        active_project="chawkidaar-core",
    )
    d = snap.to_dict()
    assert d["current_loop_number"] == 42
    assert d["current_state"] == "RUNNING"
    assert d["active_project"] == "chawkidaar-core"

    restored = LoopStateSnapshot.from_dict(d)
    assert restored.current_loop_number == 42
    assert restored.current_state == "RUNNING"
    assert restored.last_checkpoint == {"step": "compile"}


def test_file_persistence_save_load(tmp_path: Path):
    file_path = tmp_path / "sub_dir" / "test_state.json"
    persistence = FileStatePersistence(file_path=file_path)

    assert persistence.load() is None

    snap = LoopStateSnapshot(
        current_loop_number=5,
        current_state=LoopState.VERIFYING.value,
        active_project="demo_proj",
    )
    persistence.save(snap)

    assert file_path.exists()
    loaded = persistence.load()
    assert loaded is not None
    assert loaded.current_loop_number == 5
    assert loaded.current_state == "VERIFYING"
    assert loaded.active_project == "demo_proj"


def test_file_persistence_corrupted_file(tmp_path: Path):
    file_path = tmp_path / "corrupt_state.json"
    file_path.write_text("invalid json {", encoding="utf-8")

    persistence = FileStatePersistence(file_path=file_path)
    loaded = persistence.load()
    assert loaded is None


def test_file_persistence_clear(tmp_path: Path):
    file_path = tmp_path / "clear_state.json"
    persistence = FileStatePersistence(file_path=file_path)
    snap = LoopStateSnapshot(current_loop_number=1)
    persistence.save(snap)
    assert file_path.exists()

    persistence.clear()
    assert not file_path.exists()
