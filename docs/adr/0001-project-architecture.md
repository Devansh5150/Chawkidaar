# ADR 0001: Project Architecture & Configuration Schema

## Status

Accepted

## Date

2026-07-23

## Context

Chawkidaar is an autonomous AI agent monitoring and loop engineering system that coordinates AI coding agents, runs iterative verification checks, emits lifecycle events, and alerts users via Telegram.

To support arbitrary software projects and AI agent frameworks without hardcoded parameters, Chawkidaar requires a strongly typed, extensible, and validated Project Configuration Schema capable of loading project metadata, AI agent execution constraints, loop engine parameters, verification commands, and notification options from file sources (YAML/JSON) and environment variables.

## Decision

We adopt a modular, layered architecture for Chawkidaar structured as follows:

1. **Configuration Subsystem (`chawkidaar/config`)**: Built with Pydantic v2 and PyYAML. Uses hierarchical models (`ProjectMetadata`, `AgentConfig`, `LoopConfig`, `VerificationConfig`, `TelegramConfig`, `ProjectConfig`) managed by `ConfigManager`. Supports default fallbacks, schema validation, serialization, and environment variable overrides (`CHAWKIDAAR_*`).
2. **Core Loop Engine Subsystem (`chawkidaar/loops`)**: Decoupled Finite State Machine (`StateMachine`), in-memory `EventBus`, atomic file persistence (`FileStatePersistence`), and autonomous `LoopEngine`.
3. **Structured Logging (`chawkidaar/utils`)**: Structured JSON/console formatting with `EventLoggerSubscriber`.

## Alternatives Considered

1. **Raw Python Dictionaries**: Fast to prototype but lacks type safety, validation errors, autocompletion, and schema enforcement.
2. **Standard Library `dataclasses`**: Provides typing but lacks built-in environment variable resolution, validation bounds (e.g. `ge=1`), and seamless YAML parsing out-of-the-box.
3. **TOML Configuration**: Native to Python 3.11+, but YAML is more widely used across DevOps pipelines, Docker, and GitHub Actions ecosystems.

## Rationale

- **Pydantic v2**: High performance, strong validation rules (e.g., `ge=1` on timeout and max loops), JSON/dict serialization, and seamless integration with FastAPI/SQLModel.
- **PyYAML**: Human-readable hierarchical configuration files suitable for project root placement (`configs/default.yaml` or `chawkidaar.yaml`).
- **Decoupled Architecture**: Zero coupling between core loop execution, notification adapters, and configuration loaders guarantees high maintainability and testability.

## Consequences

- Configuration files are strictly validated at launch; invalid config files fail fast with clear validation messages.
- New configuration sections (e.g., GitHub integration, Agent tools) can be added as sub-models without breaking existing project configs.
