# Agent readiness checklist

This is the extracted checklist for future projects. "Included" means this base contains an implementation or reusable instruction. "Configure" means every application must supply its own values or code. "Optional" means adopt it when the project's scale or product needs it.

| Status | Capability | Location or action |
|---|---|---|
| Included | One shared instruction source for Codex and Claude | AGENTS.md and CLAUDE.md |
| Included | Portable shared client settings | .codex/config.toml and .claude/settings.json |
| Included | Local override, secret, cache, and artifact ignores | .gitignore; extend for the chosen stack |
| Included | Quiet command output with complete retained logs and exit status | tools/q.sh |
| Included | Quick/full validation and machine-readable summaries | tools/ci.sh and build/ci/ |
| Included | Setup diagnostics without global modifications | tools/setup.sh |
| Included | GitHub and GitLab CI entry points | Keep the provider used by the new project |
| Included | Task worktrees, clean-state checks, merge lock, gated fast-forward, safe cleanup | tools/wt.sh |
| Included | Task, handoff, decision, state, and role templates | docs/templates/ |
| Included | Validation and task-preparation skills for both clients | .agents/skills and .claude/skills |
| Included | Context and delegation conventions with Claude hook helpers | AGENTS.md and tools/hooks/ |
| Included | Tests for failure propagation, hook behavior, project creation, and Git lifecycle | tests/base/ |
| Configure | Product brief, architecture map, shared contracts and ownership | docs/PROJECT.md and module READMEs |
| Configure | Language versions, lockfiles, prerequisite installation, env examples | Choose stack-specific files and documented setup |
| Configure | Dev, build, lint, format, focused-test, package and release commands | Application scripts and documentation |
| Configure | Real application validation | agent-base.json checks.quick/full; require-project gate |
| Configure | Architectural boundaries enforced in code | Import restrictions, dependency DAG rules, generated-file checks |
| Configure | Test isolation | Temporary paths, databases, ports, saves, independent worktree outputs |
| Configure | Completion evidence | Behavior checks, logs, inspected visuals, documented limitations |
| Configure | External integration policy | Choose local merge versus PR gates and authorized release workflow |
| Optional | Graph navigation with coverage and freshness verification | MCP example, client setup, actual graph registry identifier |
| Optional | LSP navigation and diagnostics | Stack-specific language servers |
| Optional | Provider-specific additional skills or plugins | Install for an actual recurring workflow |
| Optional | Analyst/implementer split for large tasks | Self-contained packets with APIs and acceptance criteria |
| Optional | CI step selection and verified-result reuse | Input maps, toolchain/env keys, force-full path, invalidation tests |
| Optional | Shared compiler cache with private outputs | Stack-specific cache and correctness checks |
| Optional | Resource and long-session controls | GPU locks, concurrency caps, disk budgets, usage/context checkpointing |
| Optional | Agent-accessible application control and observation | CLI or API calling the real product operations |
| Optional | Headless, seeded, replayable scenario testing | Deterministic fixtures, clock control, snapshots and verdicts |
| Optional | Testable UI and visual regression | Stable IDs, accessibility, readiness, screenshots and browser/game runners |
| Optional | Repeatable performance checks | Baselines, representative workloads, correctness fingerprints |
| Optional | Cross-platform shipping verification | Build/package/import checks and actual target smoke tests |
| Optional | Asset generation and human review workflow | Product-specific tooling, provenance and explicit approval policy |

Use [OPTIONAL.md](OPTIONAL.md) for implementation guidance. A green starter gate does not imply the Configure or Optional rows have been implemented. Complete the fresh clone acceptance in [SETUP.md](SETUP.md).
