---
name: prepare-task
description: Prepare a self-contained implementation task packet for substantial work with dependencies, ownership boundaries, or a handoff between agents. Use when task preparation is requested or clearly needed; simple edits can proceed directly.
---

Use [the task template](../../../docs/templates/task.md). Read only the relevant product requirements and current APIs. Define the goal, observable acceptance checks, owner paths, dependencies, commands, and pitfalls. Add a concise code map so implementation starts at the right symbols.

Verify references against current code, including graph coverage when using codebase-memory. State unresolved product choices and any conflicts with the current implementation. Scale the packet to the work instead of filling it with general advice.

Save the requested packet under `docs/tasks/` unless the user named another destination. If asked only for a plan or draft, return that in chat. Preparing a task does not start workers, change ownership, or authorize implementation beyond the current request.
