# Project brief

This repository is an agent development base. Its product is the instructions, scripts, templates, and configuration used to start future projects.

- Runtime: Python standard library, Bash entry points, and Git. Python 3.10 or newer.
- Architecture: `tools/common.py` supplies configuration and Git helpers; individual tools handle logging, checks, worktrees, and project generation. `tests/base/` verifies those tools in temporary repositories.
- Shared contract: `agent-base.json` defines the project name, base branch, worktree cap, required executables, optional code graph, and application validation commands.
- Boundaries: generated projects are independent; source repositories and user-level settings remain untouched. No product-specific build cache, network service, telemetry collector, or game engine is bundled.
- Validation: `tools/ci.sh quick` validates this base. Future projects must add their own application checks.
- Release target: a local Git repository that can generate fresh project directories. No remote hosting or publishing is configured.

When starting an application, replace this brief with its purpose, selected stack and versions, module map, important invariants, shared contracts, test commands, and packaging/deployment target.
