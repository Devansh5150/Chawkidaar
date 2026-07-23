"""Configuration exceptions for Chawkidaar."""


class ConfigError(Exception):
    """Base exception for all configuration-related errors."""

    pass


class ConfigFileNotFoundError(ConfigError):
    """Raised when a configuration file is not found."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Configuration file not found at '{path}'")


class InvalidConfigFormatError(ConfigError):
    """Raised when a configuration file contains invalid YAML or JSON syntax."""

    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Invalid configuration format in '{path}': {reason}")


class ConfigValidationError(ConfigError):
    """Raised when configuration data fails schema validation."""

    def __init__(self, reason: str, errors: list | None = None):
        self.reason = reason
        self.errors = errors or []
        super().__init__(f"Configuration schema validation failed: {reason}")
