"""Claude context guard. Best effort, fail open, and never execute shell input."""
import json
import os
from pathlib import Path
import shlex
import sys

CODE_SUFFIXES = {".py", ".rs", ".gd", ".sh", ".js", ".jsx", ".ts", ".tsx", ".go", ".c", ".cpp", ".h", ".cs", ".gdshader"}


def reason(event):
    inp = event.get("tool_input") or {}
    path = None
    if event.get("tool_name") == "Read" and not inp.get("limit"):
        path = inp.get("file_path")
    elif event.get("tool_name") == "Bash":
        # Only inspect simple cat calls. Shell pipelines and compound commands
        # need a real shell parser; guessing would block legitimate workflows.
        words = shlex.split(inp.get("command", ""))
        if len(words) == 3 and words[:2] == ["cat", "--"]:
            words = [words[0], words[2]]
        if len(words) == 2 and words[0] == "cat":
            path = words[1]
    if not path:
        return None
    path = Path(path)
    if not path.is_absolute():
        path = Path(event.get("cwd") or os.getcwd()) / path
    if path.suffix not in CODE_SUFFIXES:
        return None
    limit = int(os.environ.get("AGENT_READ_MAX_LINES", "200"))
    with path.open("rb") as source:
        count = sum(1 for _ in source)
    if count > limit:
        return (f"This code file has {count} lines. Read an outline and the relevant sections. "
                "Use a symbol snippet or Read with offset and limit. If most of the file is "
                "needed, use an explicit limit. See AGENTS.md.")
    return None


if __name__ == "__main__":
    try:
        message = reason(json.load(sys.stdin))
        if message:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                "permissionDecision": "deny", "permissionDecisionReason": message}}))
    except (ValueError, OSError, TypeError, AttributeError):
        pass
