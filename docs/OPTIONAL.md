# Optional capabilities

These are extracted design requirements for features whose implementation depends on the future product. The base supplies the portable workflow; add these deliberately as the application grows.

## Build and CI efficiency

Start with private outputs per worktree. If compilation becomes expensive, add a content-addressed compiler cache whose keys cover sources, generated/include inputs, dependencies, features, compiler/linker versions, and relevant environment. Test restoration against clean compilation. Avoid a shared mutable output directory whose binaries can change under another agent's tests.

Path-selected CI needs a maintained input map and an all-checks fallback for unknown paths or changed infrastructure. A reusable green result must identify the tested content and environment, reject dirty/untracked input, and invalidate on meaningful toolchain or input changes. Documentation is exempt only when no check reads it. The base always reruns its gate; it does not assume these optimizations are safe for an unknown stack.

## Resources and long sessions

Use a process-scoped OS lock for exclusive resources, including GPUs and hardware devices. Record which launchers already lock. Bound concurrent worktrees and test workers. For disk management, report usage first; prune only owned caches and outputs, under appropriate locks, without touching active runs.

Usage limits and context budgets belong to the chosen client and account. Use them to trigger a meaningful checkpoint and handoff, not to silently reduce the requested feature. Keep task/agent state in an optional local ledger derived from the state template. Avoid importing provider-specific transcript paths, account tokens, or old session identifiers into the project.

## Application control for agents

Expose the product's real actions and observations through a CLI or structured API. Publish schemas, stable object identifiers, units, capability discovery, and actionable errors. Actions call the same validation and domain operations as the human interface. Separate debug-only commands and record their use.

A CLI operating on an isolated session directory often suffices for a small simulation. A persistent hub becomes useful for interactive sessions, event streams, or multiple tools controlling a long-lived process. Either design needs session isolation, lifecycle commands, timeouts, and artifact locations. Keep binary artifacts in files and return paths.

Add headless operation, controlled time, seeded fixtures, snapshot/restore, deterministic replays, and scenario setup/actions/checks where the domain supports them. Each new user action should have an automation route and a meaningful scenario. Structured verdicts should distinguish failure, skipped checks, warnings, and complete success.

## UI, performance, and release

Give interactive controls stable automation IDs and accessible names. Readiness signals should reflect completed data loading. Test on the actual target when graphics/platform behavior matters; use screenshots and clips for visual review, and inspect them before reporting success.

Use a committed performance workload, known hardware conditions, and stable baselines. Keep wall-clock performance gates away from heavily contended correctness runs. For pure optimization, verify unchanged results alongside better timings. State measured overages and tradeoffs instead of removing requested behavior to satisfy a budget.

For cross-platform releases, pin the toolchain and check the packaged artifact's dependencies. Include clean-machine smoke tests for failures that compilation cannot catch. Rust/Windows linker flags, Godot launchers, Blender pipelines, and renderer-specific budgets must be selected for the new stack rather than copied wholesale.
