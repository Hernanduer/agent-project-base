# Development workflow

For a small change, inspect the relevant code, implement, run appropriate checks, and report the outcome. Use a task packet for work whose scope, dependencies, or handoff needs justify one. The [task template](templates/task.md) captures acceptance checks, owner paths, relevant APIs, and execution steps. An analyst can prepare it before implementation when that saves repeated exploration.

## Worktrees and integration

With concurrent agents, use one task branch and worktree per owner. The optional local workflow requires a clean, committed base branch checked out in its own directory:

```bash
tools/wt.sh new feature-name
# Enter the printed directory. Implement, validate, and commit your files there.
tools/wt.sh sync
tools/ci.sh quick
tools/wt.sh merge
# From the main checkout after a successful merge:
tools/wt.sh rm feature-name
```

`new` uses `task/<name>` and a sibling `<repo-name>-wt/<name>` directory. `max_worktrees` limits active task branches with checkouts. Repeating `new` for an existing task prints its location. `sync` rebases onto the configured local base branch. No command fetches, pushes, or rewrites the base branch.

`merge` takes a lock in the shared Git directory, rebases the task, runs its quick gate, checks for dirty state or moved branches, then fast-forwards the base. A failed gate leaves the base branch untouched by this helper. Rebase conflicts stay available for normal Git resolution; finish or abort the rebase before retrying. If the base or task moves during the gate, retry so it is validated again. All local integrators should use the same lock; arbitrary external Git writers cannot be completely coordinated by this helper.

`rm` refuses uncommitted work and unmerged commits. It removes the worktree, its ignored build outputs, and its merged task branch. There is deliberately no force-delete option. Run cleanup from the base checkout, not inside the directory being removed.

For hosted projects, branch/PR protection and required CI can own integration instead. You can still use `new` and `ls` for isolation. Choose the integration policy in PROJECT.md. The starter has no CI result reuse, path-based selection, remote merge automation, or shared compiler cache; add these only with correctness tests for invalidation and concurrency.

## Ownership and shared resources

State owner paths and shared-contract owners in each brief. Tell workers who else is active and require them to preserve concurrent edits. Use [analyst](templates/analyst.md), [implementer](templates/implementer.md), and [finisher](templates/finisher.md) briefs as needed. Only the main session delegates.

Build outputs belong to each worktree. Keep temporary files, ports, test databases, save directories, and generated artifacts isolated. Use process-scoped locks for exclusive GPU, device, or deployment resources. Document whether a tool already locks internally to avoid deadlocks. Stop servers and monitors started for a completed task.

## Evidence and handoff

Validation should establish the acceptance behavior, including relevant failure cases and platform builds. Record command results and artifact paths. Review visual evidence before citing it. Performance measurements should use repeatable workloads and known conditions, with correctness fingerprints where appropriate.

Update docs when behavior, architecture, commands, or decisions change. Significant decisions can use [the decision template](templates/decision.md). On pause, preserve meaningful work and use [the handoff template](templates/handoff.md). A successor reads the handoff and branch before repeating exploration. Keep temporary orchestration state separate from durable project decisions; [the state template](templates/state.md) is optional.
