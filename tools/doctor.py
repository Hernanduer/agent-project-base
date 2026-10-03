"""Check the local environment without installing or modifying anything."""
import argparse
import shutil
import sys

from common import ROOT, config, git


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-project", action="store_true")
    args = parser.parse_args()
    data = config()
    missing = []
    for name in dict.fromkeys(["git", "bash", "python3", *data["required_tools"]]):
        path = shutil.which(name)
        print(f"[{'ok' if path else 'missing'}] {name}: {path or 'install and add to PATH'}")
        if not path:
            missing.append(name)
    if sys.version_info < (3, 10):
        missing.append("Python >= 3.10")
    for name in ("codex", "claude", "codebase-memory-mcp"):
        path = shutil.which(name)
        print(f"[{'available' if path else 'optional'}] {name}: {path or 'not on PATH'}")
    graph = data["code_graph"]
    if graph["required"] and not shutil.which("codebase-memory-mcp"):
        missing.append("required codebase-memory-mcp executable")
    print(f"[graph] project={graph['project'] or 'not configured'}; verify connection and index in each client")
    if shutil.which("git"):
        result = git(ROOT, "rev-parse", "--show-toplevel", check=False)
        print(f"[git] {result.stdout.strip() if result.returncode == 0 else 'not initialized; run git init -b main'}")
    if not data["checks"]["quick"]:
        print("[setup] application checks are not configured; edit agent-base.json")
        if args.require_project:
            missing.append("application quick checks")
    print("[setup] review docs/SETUP.md; client trust, hooks, and MCP are checked interactively")
    return 1 if missing else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        sys.exit(f"[doctor] {exc}")
