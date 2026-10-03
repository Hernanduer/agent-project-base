---
name: check-project
description: Run this repository's configured validation and explain failures or missing application checks when asked to test, validate, or prepare a completed change for integration.
---

Read the command contract in `agent-base.json` and the relevant part of [the workflow](../../../docs/WORKFLOW.md). Run a focused check when diagnosing a specific issue; use `tools/ci.sh quick` for the completion gate and `full` when the changed behavior warrants its slower checks.

If application quick checks are empty, explicitly report that only starter tooling is covered. Use `--require-project` when checking application readiness. Fix failures within the requested scope and rerun affected checks. Inspect the saved log around the error rather than printing it whole. Never weaken a check to make a result green.

Report checks run, outcome, evidence paths, and any unverified behavior. Passing checks alone do not authorize a merge, deployment, or external publication beyond the user's existing request.
