# Set up a new project

Run `python3 tools/new_project.py ../my-project --name my-project` from a clean, committed copy of this base. Enter the generated directory and complete the steps below. The generator intentionally leaves the first commit to you so it can describe the actual project.

1. Replace [PROJECT.md](PROJECT.md) with the product brief and architecture map. Add module READMEs as the code grows.
2. Select and pin the actual language/runtime toolchain, dependency lockfiles, and formatter/linter configuration. The base's Python requirement covers its own tools only.
3. Edit `agent-base.json`. Set `required_tools` to the executables the build needs. Add real application checks under `checks.quick`; add expensive integration, platform, replay, or performance checks under `checks.full`.
4. Install dependencies using the project's documented commands. `tools/setup.sh` checks prerequisites; it does not install them.
5. Run `tools/setup.sh --require-project` and `tools/ci.sh quick --require-project`. Then launch each agent client and check its instructions, skill discovery, and optional tools.
6. Keep the CI definition for your hosting provider. After configuring the application, add `--require-project` to its CI command so later accidental removal of application checks fails.
7. Make the first commit. Add a remote only when you choose one.

An example command configuration for an npm application:

```json
"checks": {
  "quick": [
    {"name": "typecheck", "argv": ["npm", "run", "typecheck"]},
    {"name": "lint", "argv": ["npm", "run", "lint"]},
    {"name": "tests", "argv": ["npm", "test"]}
  ],
  "full": [{"name": "browser tests", "argv": ["npm", "run", "e2e"]}]
}
```

Each `argv` is an argument array, executed from the repository root without a shell. Use a checked-in script for pipelines, environment setup, or package-local commands. Quick always includes starter validation and `tests/base`; full includes quick and then the full list. The gate stops at the first failure and writes a unique JSON summary under `build/ci/` with full log paths. It does not cache results or skip checks based on changed paths.

## Codex and Claude

Codex reads `AGENTS.md`; `CLAUDE.md` imports that same file. Keep shared rules there and detailed, conditional workflow material in docs or skills. Models, account settings, and credentials belong in user configuration.

The committed `.codex/config.toml` sets workspace-write sandboxing and on-request approvals. Project configuration requires the client's project trust. The committed `.claude/settings.json` registers two portable hooks using `CLAUDE_PROJECT_DIR`: a large-read context guard and a nested-delegation guard. Personal overrides stay in ignored `.claude/settings.local.json`. See the official [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-basic), [Claude settings](https://code.claude.com/docs/en/settings), and [hook reference](https://code.claude.com/docs/en/hooks).

Commit attribution is disabled in the shared Claude settings (`attribution.commit` is empty and `attribution.sessionUrl` is false). AGENTS.md also tells both clients to omit AI co-author trailers, session URLs, and generated-by taglines. New projects inherit this preference.

Skills are maintained in `.agents/skills/` and mirrored as regular files in `.claude/skills/`. After editing a skill, run `python3 tools/sync_skills.py`; CI checks for drift. Avoiding symlinks makes copies and Git checkouts work without symlink privileges. To remove a skill, remove both copies. These simple skills have no supporting assets; extend the sync tool if you add them. Discovery locations: [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Claude skills](https://code.claude.com/docs/en/skills).

## Optional code graph

Install the trusted `codebase-memory-mcp` executable using that project's instructions and confirm it is on PATH. For Claude, copy `.mcp.json.example` to `.mcp.json` if the project does not already have MCP configuration; otherwise merge the server entry. For Codex, uncomment the matching server block in `.codex/config.toml`. These files contain executable registrations, never credentials.

Index the primary checkout using the installed tool's API and use the returned registry identifier for `code_graph.project` in `agent-base.json`. Set `code_graph.required` to true if this is a project prerequisite. Record its refresh behavior and checkout coverage in PROJECT.md. Never copy another repository's identifier or index every task worktree. Check connection and index status in each client. `doctor` checks the executable and declared configuration; it does not claim to test an MCP connection or inspect the index.

## Fresh clone acceptance

- Setup succeeds with documented prerequisites, without relying on another developer's home paths.
- Each client can state the shared instructions and discover the two repo skills.
- Claude can run a normal small read; its read guard returns a useful correction for a large unrestricted read. An explicit bounded read remains available.
- Configured MCP servers connect; an indexed symbol lookup succeeds if graph support is enabled.
- A focused application test and the quick gate run, and their logs are discoverable.
- Worktrees have independent outputs, ports, and runtime data where needed.

These interactive client checks require an authenticated client. The automated tests verify hook payloads and scripts, not a live Claude or Codex session.
