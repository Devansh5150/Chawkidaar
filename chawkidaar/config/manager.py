"""Configuration Loader and Manager for Chawkidaar.

Provides loading and saving of ProjectConfig from YAML and JSON files, with
strict exception handling for missing files, invalid syntax, and schema failures.
"""

import json
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from chawkidaar.config.exceptions import (
    ConfigFileNotFoundError,
    ConfigValidationError,
    InvalidConfigFormatError,
)
from chawkidaar.config.schema import ProjectConfig


class ConfigManager:
    """Manages project configuration lifecycle supporting YAML and JSON files."""

    def __init__(self, config_path: Optional[str | Path] = None):
        self.config_path = Path(config_path) if config_path else None
        self._config: Optional[ProjectConfig] = None

    @property
    def config(self) -> ProjectConfig:
        """Return loaded ProjectConfig instance or load default if not initialized."""
        if self._config is None:
            if self.config_path and self.config_path.exists():
                self._config = self.load_config(self.config_path)
            else:
                self._config = self.get_default_config()
        return self._config

    @staticmethod
    def get_default_config() -> ProjectConfig:
        """Create and return a default ProjectConfig instance."""
        return ProjectConfig()

    def load_config(self, file_path: str | Path) -> ProjectConfig:
        """Load configuration from a YAML or JSON file.

        Raises:
            ConfigFileNotFoundError: If the file path does not exist.
            InvalidConfigFormatError: If syntax parsing fails.
            ConfigValidationError: If schema validation fails.
        """
        path = Path(file_path)
        if not path.exists():
            raise ConfigFileNotFoundError(str(path))

        ext = path.suffix.lower()
        try:
            with open(path, "r", encoding="utf-8") as f:
                if ext == ".json":
                    raw_data = json.load(f)
                else:
                    raw_data = yaml.safe_load(f)
        except (json.JSONDecodeError, yaml.YAMLError) as err:
            raise InvalidConfigFormatError(str(path), str(err)) from err
        except Exception as err:
            raise InvalidConfigFormatError(str(path), str(err)) from err

        if raw_data is None:
            raw_data = {}

        if not isinstance(raw_data, dict):
            raise InvalidConfigFormatError(
                str(path), "Configuration content must be a valid key-value mapping"
            )

        try:
            self._config = ProjectConfig.model_validate(raw_data)
            return self._config
        except ValidationError as err:
            raise ConfigValidationError(
                reason=str(err), errors=err.errors()
            ) from err

    def save_config(
        self, config: ProjectConfig, file_path: str | Path
    ) -> None:
        """Save ProjectConfig instance to a YAML or JSON file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        ext = path.suffix.lower()
        data = config.model_dump()

        with open(path, "w", encoding="utf-8") as f:
            if ext == ".json":
                json.dump(data, f, indent=2)
            else:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
