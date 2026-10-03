# Agent project base

A small foundation for projects developed with Codex and Claude Code. It extracts the shared working practices from Transporter and related repositories into portable instructions, tested utilities, and optional workflow guides. It has no application framework or game engine dependency.

Requires Python 3.10+, Bash, and Git. Local worktree merge locking requires Linux, macOS, or WSL. No Python packages are needed for the supplied tooling.

```bash
tools/setup.sh
tools/ci.sh quick
python3 tools/new_project.py ../my-project --name my-project
```

The generator requires a clean, committed starter. It refuses an existing destination, copies tracked files only, and initializes a separate Git repository with no remote or initial commit. Ignored logs and local settings are omitted. Keep credentials out of tracked files.

In the new project, describe the product in [docs/PROJECT.md](docs/PROJECT.md), configure real application checks in [agent-base.json](agent-base.json), and follow [docs/SETUP.md](docs/SETUP.md). Run `tools/ci.sh quick --require-project` before considering the application configured. The uncustomized base explicitly reports **STARTER ONLY**: its green result verifies the starter tooling, not a future application.

| Included | Entry point |
|---|---|
| Shared Codex and Claude instructions | [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md) |
| Client configuration and optional MCP setup | [Setup guide](docs/SETUP.md) |
| Quiet commands, validation, diagnostics | `tools/q.sh`, `tools/ci.sh`, `tools/setup.sh` |
| Worktree creation, synchronization, validated local merges, cleanup | `tools/wt.sh` |
| Task preparation and project validation skills for both clients | [.agents/skills](.agents/skills), [.claude/skills](.claude/skills) |
| Tasks, handoffs, decisions, and role briefs | [Workflow](docs/WORKFLOW.md), [templates](docs/templates) |
| Complete extracted capability checklist | [Checklist](docs/CHECKLIST.md) |
| Parallel builds, resource limits, agent APIs, and visual testing | [Optional capabilities](docs/OPTIONAL.md) |
| Source mapping and deliberate adaptations | [Origins](docs/ORIGINS.md) |

GitHub Actions and GitLab CI definitions call the same local validation command. Keep the file for your chosen host. The tools do not install packages, change global agent settings, publish anything, or start background monitors.
