"""Shared configuration and process helpers; Python standard library only."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def config(root=ROOT):
    data = json.loads((root / "agent-base.json").read_text())
    if data.get("version") != 1:
        raise ValueError("agent-base.json: expected version 1")
    for key in ("project", "base_branch"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"agent-base.json: {key} must be a nonempty string")
    if type(data.get("max_worktrees")) is not int or data["max_worktrees"] < 1:
        raise ValueError("max_worktrees must be a positive integer")
    required = data.get("required_tools")
    if not isinstance(required, list) or any(not isinstance(x, str) or not x for x in required):
        raise ValueError("required_tools must be a list of executable names")
    graph = data.get("code_graph", {})
    if not isinstance(graph, dict) or type(graph.get("required")) is not bool:
        raise ValueError("code_graph.required must be a boolean")
    if graph.get("project") is not None and not isinstance(graph["project"], str):
        raise ValueError("code_graph.project must be a string or null")
    if graph["required"] and not graph.get("project"):
        raise ValueError("required code graph needs a project identifier")
    checks = data.get("checks")
    if not isinstance(checks, dict):
        raise ValueError("checks must contain quick and full lists")
    for lane in ("quick", "full"):
        if not isinstance(checks.get(lane), list):
            raise ValueError(f"checks.{lane} must be a list")
        for step in checks[lane]:
            if not isinstance(step, dict) or not isinstance(step.get("name"), str) or not step["name"]:
                raise ValueError(f"checks.{lane}: every step needs a name")
            argv = step.get("argv")
            if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or not x for x in argv):
                raise ValueError(f"{step['name']}: argv must be a nonempty list of strings")
    return data


def git(root, *args, check=True):
    return subprocess.run(["git", "-C", str(root), *args], text=True,
                          capture_output=True, check=check)


def clean(root):
    return not git(root, "status", "--porcelain", "--untracked-files=all").stdout.strip()
