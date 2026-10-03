# Sources and adaptations

Extracted on 2026-10-03 from the owner's local repositories. Transporter was the primary baseline; sibling projects supplied complementary patterns. Paths below identify the original source inside each repository and are provenance, not runtime dependencies.

| Source | Extracted into this base |
|---|---|
| transporter/AGENTS.md and CLAUDE.md | Shared instructions, graph-first structural navigation, coverage verification, bounded source reads |
| transporter/docs/tech/AGENT_RULES.md | Worktree ownership, integration gates, resource isolation, quiet output, completion evidence, handoffs |
| transporter/tools/q.sh | Quiet command runner concept, retained output, original exit status; rewritten in Python for bounded generic output |
| transporter/tools/wt.sh | Task worktree lifecycle and serialized gated fast-forward; rewritten without Rust, Godot, cache, or fixed-path dependencies |
| transporter/tools/ci.sh | One quick/full validation interface with retained logs and structured results; application commands are configurable |
| transporter/.orchestration/read_gate.py and no_nested_agents.py | Portable Claude hooks; removed fixed usernames, graph IDs, and provider log paths |
| transporter/docs/tech/TASK_PACKETS.md and .orchestration/templates/ | Short task, ownership, analyst, implementer, finisher, and handoff templates |
| transporter/docs/tech/AGENT_LAYER.md and ARCHITECTURE.md | Optional agent API, scenario, visual, UI-readiness, performance, and release requirements |
| ter/AGENTS.md and mise.toml | Module documentation maps, shared contracts, tool versions, LSP as a complementary tool |
| microbio/CLAUDE.md, .eslintrc.cjs, package.json, playwright.config.ts | Executable architecture boundaries, one check command, ownership, isolated browser runs |
| silhouette/.github/workflows/ci.yml | Hosted CI, architecture checks, target build and dependency verification |
| long_horizon/.gitlab-ci.yml and .githooks/pre-commit | Server-side validation alongside local checks; optional local hooks need clone setup |
| long_horizon/docs/agent_mode.md | A simple headless CLI with isolated, inspectable session state |
| beeciety_real/AGENTS.md | Repeatable profiling with correctness fingerprints and headless domain separation |
| beeciety/AGENTS.md | Stable build-cache environment; concise reporting and documentation proportional to a change |
| astrogazer/AGENTS.md | Consult documentation for the exact framework version selected by the project |

New glue supplied during extraction: `agent-base.json`, environment diagnostics, project generator, skill mirroring, configuration/link checks, and regression tests. Optional guides preserve useful requirements without claiming to implement an application-specific system.

Excluded from the base: repository history, application code/assets, saved sessions, credentials, local permission accumulations, fixed home paths, hard-coded session attribution, mandatory model assignments, particular performance limits, automatic account-usage monitoring, shared Rust caches, and game-specific tools.

The client's instruction/skill discovery and settings locations were checked against official documentation linked in SETUP.md. The scripts and hook payloads are locally tested; a logged-in live session in each client remains part of new-project acceptance.
