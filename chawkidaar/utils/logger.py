"""Structured Logging System for Chawkidaar.

Provides JSON or structured console logging for state transitions, execution times,
errors, and recovery events.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from chawkidaar.loops.events import EventBus, LoopEvent


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured output."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "payload") and record.payload:
            log_obj["payload"] = record.payload
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def get_logger(name: str = "chawkidaar", json_format: bool = False) -> logging.Logger:
    """Configure and return a structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if json_format:
            handler.setFormatter(JSONFormatter())
        else:
            fmt = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class EventLoggerSubscriber:
    """Subscribes to an EventBus to automatically log all loop lifecycle events."""

    def __init__(
        self,
        logger: logging.Logger | None = None,
        event_bus: EventBus | None = None,
    ):
        self.logger = logger or get_logger("chawkidaar.event_logger")
        if event_bus:
            self.attach(event_bus)

    def attach(self, event_bus: EventBus) -> None:
        """Attach subscriber to an EventBus."""
        event_bus.subscribe(None, self.on_event)

    def on_event(self, event: LoopEvent) -> None:
        """Handle incoming event and log structured info."""
        msg = (
            f"EVENT [{event.event_type}] | Loop #{event.loop_number} | "
            f"Project: '{event.project_name}'"
        )
        if event.payload:
            msg += f" | Payload: {event.payload}"
        self.logger.info(msg)
