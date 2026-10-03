# Working in this repository

Read [docs/PROJECT.md](docs/PROJECT.md) for the product and architecture. Use [docs/WORKFLOW.md](docs/WORKFLOW.md) for task ownership, validation, and handoffs. Read only the sections relevant to the task.

## Commands

- `tools/setup.sh`: check local prerequisites and report setup gaps.
- `tools/q.sh <command> [args...]`: retain a complete log and print a bounded result; run from the directory the command expects.
- `tools/ci.sh quick`: validate the starter plus application checks configured in `agent-base.json`.
- `tools/ci.sh full`: quick checks plus configured slower checks.
- `tools/ci.sh quick --require-project`: refuse an unconfigured application gate.
- `tools/wt.sh new|ls|sync|merge|rm [task]`: optional local worktree workflow.

If the gate reports STARTER ONLY, it has not validated application behavior. Add appropriate project checks when establishing the stack. Never substitute an empty or always-successful command for a required check.

## Navigation and context

For structural questions, use codebase-memory when configured and available. Read `code_graph.project` from `agent-base.json`; check index status, find symbols, trace relevant relationships, then read snippets. Check coverage for relied-on paths. Verify negative or exhaustive conclusions with source searches. If the graph is unavailable or stale, use direct source inspection and state that limitation.

Document whether the graph covers the main checkout or the working tree. Never assume it contains uncommitted or worktree changes, and do not index each task worktree. Use `rg` for literals, configuration, documentation, and source verification. LSP can supplement navigation and diagnostics.

Outline large files and read relevant sections. Use quiet output for builds and tests, then inspect saved failure logs. Avoid repeating successful checks unless changes or new evidence justify them.

## Changes and ownership

Follow the user's current scope and existing authorization. Make ordinary, reversible implementation decisions and complete the work. Explain concrete blockers rather than adding routine confirmation steps. External publication or messages require the user's authorization.

With concurrent work, use a separate worktree and define owner paths. Preserve other people's edits. Shared contracts and integration files need explicit ownership. Stage only your changes; never rewrite main or force-push as part of the routine workflow.

The main session may delegate when appropriate and authorized. Workers do their own assigned work and return a handoff if it exceeds their scope; they do not launch nested agents. Each brief states responsibilities and concurrent work. Model choice stays in user configuration.

## Verification and completion

Run checks relevant to the change and the configured completion gate. Prefer tests of observable behavior and meaningful invariants. Use isolated paths, ports, and mutable data. Keep timing benchmarks separate from correctness checks on busy machines.

Report what changed, evidence, and remaining limitations. Inspect any screenshot you cite. Keep architectural decisions and changed operational instructions current; routine small edits need no new report or task packet. Comments should explain why.

Stop processes you started unless the user asked to retain them, and report any retained process. For an interrupted substantial task, preserve work and write a concise handoff using [the template](docs/templates/handoff.md).

The Claude hooks reinforce context and delegation conventions. They are best-effort helpers, not a security boundary, and do not run in Codex. Shared scripts, tests, and CI provide the cross-client validation.
