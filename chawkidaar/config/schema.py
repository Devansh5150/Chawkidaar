"""Project Configuration Schema for Chawkidaar.

Defines Pydantic v2 configuration models for project metadata, AI agent settings,
loop engine options, verification commands, and notification channels.
"""

from typing import List

from pydantic import BaseModel, Field


class ProjectMetadata(BaseModel):
    """Metadata describing the target project and environment."""

    name: str = Field(default="Chawkidaar", description="Project name")
    version: str = Field(default="0.1.0", description="Project version")
    description: str = Field(
        default="Production-Grade Autonomous AI Monitoring & Agent System",
        description="Project summary description",
    )
    environment: str = Field(default="development", description="Execution environment")


class AgentConfig(BaseModel):
    """Configuration for AI agent execution."""

    agent_type: str = Field(
        default="antigravity",
        description="Coding agent framework identifier (e.g. antigravity, claude)",
    )
    model: str = Field(default="gemini-3.6-flash", description="AI Model identifier")
    max_loops: int = Field(
        default=10, ge=1, description="Maximum allowed loop iterations per task"
    )
    timeout_seconds: int = Field(
        default=600, ge=1, description="Execution timeout per step in seconds"
    )


class LoopConfig(BaseModel):
    """Configuration for the Core Loop Execution Engine."""

    auto_verify: bool = Field(
        default=True, description="Automatically run verification after task execution"
    )
    max_retries: int = Field(
        default=3, ge=0, description="Max retries upon verification failure"
    )
    state_file_path: str = Field(
        default=".chawkidaar/state.json", description="Path to state snapshot file"
    )
    checkpoint_dir: str = Field(
        default=".chawkidaar/checkpoints", description="Directory for checkpoints"
    )


class VerificationConfig(BaseModel):
    """Configuration for project automated verification commands."""

    test_command: str = Field(default="pytest", description="Test suite command")
    lint_command: str = Field(default="ruff check .", description="Code linter command")
    type_check_command: str = Field(
        default="mypy .", description="Type checker command"
    )


class TelegramConfig(BaseModel):
    """Configuration for Telegram bot notifications."""

    enabled: bool = Field(default=False, description="Enable Telegram notifications")
    bot_token: str = Field(default="", description="Telegram Bot API Token")
    chat_id: str = Field(default="", description="Telegram Chat ID for alerts")
    notification_events: List[str] = Field(
        default_factory=lambda: [
            "LoopStarted",
            "VerificationPassed",
            "VerificationFailed",
            "WaitingForApproval",
            "LoopApproved",
            "LoopFailed",
        ],
        description="Events that trigger Telegram alerts",
    )


class ProjectConfig(BaseModel):
    """Root configuration model assembling all sub-configurations."""

    project: ProjectMetadata = Field(default_factory=ProjectMetadata)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    loop: LoopConfig = Field(default_factory=LoopConfig)
    verification: VerificationConfig = Field(default_factory=VerificationConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
