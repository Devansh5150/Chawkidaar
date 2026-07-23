"""Unit tests for Configuration Loader and Manager."""

from pathlib import Path

import pytest

from chawkidaar.config.exceptions import (
    ConfigFileNotFoundError,
    ConfigValidationError,
    InvalidConfigFormatError,
)
from chawkidaar.config.manager import ConfigManager
from chawkidaar.config.schema import (
    AgentConfig,
    LoopConfig,
    ProjectConfig,
    ProjectMetadata,
    TelegramConfig,
    VerificationConfig,
)


def test_get_default_config():
    config = ConfigManager.get_default_config()
    assert isinstance(config, ProjectConfig)
    assert isinstance(config.project, ProjectMetadata)
    assert config.project.name == "Chawkidaar"
    assert isinstance(config.agent, AgentConfig)
    assert config.agent.max_loops == 10
    assert isinstance(config.loop, LoopConfig)
    assert config.loop.auto_verify is True
    assert isinstance(config.verification, VerificationConfig)
    assert isinstance(config.telegram, TelegramConfig)


def test_load_valid_yaml_file():
    default_yaml = Path("configs/default.yaml")
    assert default_yaml.exists()

    mgr = ConfigManager()
    cfg = mgr.load_config(default_yaml)

    assert cfg.project.name == "Chawkidaar"
    assert cfg.agent.agent_type == "antigravity"
    assert cfg.loop.max_retries == 3


def test_load_valid_json_file(tmp_path: Path):
    json_path = tmp_path / "valid_config.json"
    mgr = ConfigManager()
    default_cfg = mgr.get_default_config()
    default_cfg.project.name = "JSONProject"

    mgr.save_config(default_cfg, json_path)
    assert json_path.exists()

    loaded_cfg = mgr.load_config(json_path)
    assert loaded_cfg.project.name == "JSONProject"


def test_save_load_round_trip_yaml(tmp_path: Path):
    yaml_path = tmp_path / "roundtrip.yaml"
    mgr = ConfigManager()

    cfg = mgr.get_default_config()
    cfg.project.name = "RoundtripYaml"
    cfg.agent.max_loops = 15

    mgr.save_config(cfg, yaml_path)
    reloaded = mgr.load_config(yaml_path)

    assert reloaded.project.name == "RoundtripYaml"
    assert reloaded.agent.max_loops == 15


def test_save_load_round_trip_json(tmp_path: Path):
    json_path = tmp_path / "roundtrip.json"
    mgr = ConfigManager()

    cfg = mgr.get_default_config()
    cfg.project.name = "RoundtripJson"
    cfg.agent.timeout_seconds = 1200

    mgr.save_config(cfg, json_path)
    reloaded = mgr.load_config(json_path)

    assert reloaded.project.name == "RoundtripJson"
    assert reloaded.agent.timeout_seconds == 1200


def test_missing_file_raises_exception():
    mgr = ConfigManager()
    missing_path = Path("non_existent_config.yaml")

    with pytest.raises(ConfigFileNotFoundError) as exc_info:
        mgr.load_config(missing_path)

    assert "non_existent_config.yaml" in str(exc_info.value)


def test_invalid_yaml_syntax_raises_exception(tmp_path: Path):
    bad_yaml = tmp_path / "invalid_syntax.yaml"
    bad_yaml.write_text("project:\n  name: [unclosed list", encoding="utf-8")

    mgr = ConfigManager()
    with pytest.raises(InvalidConfigFormatError) as exc_info:
        mgr.load_config(bad_yaml)

    assert "invalid_syntax.yaml" in str(exc_info.value)


def test_invalid_json_syntax_raises_exception(tmp_path: Path):
    bad_json = tmp_path / "invalid_syntax.json"
    bad_json.write_text("{invalid json", encoding="utf-8")

    mgr = ConfigManager()
    with pytest.raises(InvalidConfigFormatError) as exc_info:
        mgr.load_config(bad_json)

    assert "invalid_syntax.json" in str(exc_info.value)


def test_non_mapping_content_raises_exception(tmp_path: Path):
    list_yaml = tmp_path / "list_content.yaml"
    list_yaml.write_text("- item1\n- item2\n", encoding="utf-8")

    mgr = ConfigManager()
    with pytest.raises(InvalidConfigFormatError) as exc_info:
        mgr.load_config(list_yaml)

    assert "must be a valid key-value mapping" in str(exc_info.value)


def test_invalid_schema_raises_exception(tmp_path: Path):
    bad_schema_yaml = tmp_path / "invalid_schema.yaml"
    # max_loops is 0, which violates ge=1 constraint
    bad_schema_yaml.write_text("agent:\n  max_loops: 0\n", encoding="utf-8")

    mgr = ConfigManager()
    with pytest.raises(ConfigValidationError) as exc_info:
        mgr.load_config(bad_schema_yaml)

    assert "validation failed" in str(exc_info.value)
    assert len(exc_info.value.errors) > 0
