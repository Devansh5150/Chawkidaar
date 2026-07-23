# Context Builder Architecture

## Overview

The Context Builder aggregates repository files, diffs, configuration schema, recent execution history, and test logs into an optimized context payload passed to AI coding agents.

## Workflow

1. Scan active repository files.
2. Filter irrelevant paths via `.gitignore`.
3. Assemble prompt context containing task objectives, execution contracts, and current project configuration.
