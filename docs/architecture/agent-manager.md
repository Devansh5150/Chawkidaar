# Agent Manager Architecture

## Overview

The Agent Manager controls agent selection, execution sandboxing, timeout enforcement, and tool dispatching for AI agents (Antigravity, Claude, custom CLI tools).

## Interfaces

- `AgentAdapter`: Interface for initializing agent sessions, streaming prompts, and retrieving code modifications.
- `AgentManager`: Factory for instantiating and configuring agent adapters based on `ProjectConfig`.
