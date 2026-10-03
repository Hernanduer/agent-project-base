"""Copy a clean, tracked starter into a new directory and initialize independent Git history."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from common import ROOT, clean, git


def create(destination, name):
    destination = Path(destination).expanduser().absolute()
    if destination.exists():
        raise ValueError(f"destination already exists; nothing changed: {destination}")
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("choose a destination outside the starter repository")
    if not name.strip():
        raise ValueError("project name cannot be empty")
    git(ROOT, "rev-parse", "--verify", "HEAD")
    if not clean(ROOT):
        raise ValueError("commit the starter's changes before generating a project")
    files = git(ROOT, "ls-files", "-z").stdout.split("\0")
    for relative in filter(None, files):
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"expected a regular tracked file: {relative}")
    destination.mkdir(parents=True)
    # On a copy error, preserve the partial destination for inspection rather
    # than recursively deleting a directory another process might have used.
    for relative in filter(None, files):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    settings = destination / "agent-base.json"
    data = json.loads(settings.read_text())
    data.update(project=name, base_branch="main")
    data["code_graph"] = {"project": None, "required": False}
    data["required_tools"] = []
    data["checks"] = {"quick": [], "full": []}
    settings.write_text(json.dumps(data, indent=2) + "\n")
    # Escape line breaks in prose; the configured name remains verbatim in JSON.
    title = name.replace("\r", " ").replace("\n", " ")
    (destination / "docs" / "PROJECT.md").write_text(
        f"# {title}\n\nProject brief: define the product, stack, architecture, invariants, and release target here.\n\n"
        "Configure application checks in `agent-base.json`, then follow [setup](SETUP.md).\n")
    git(destination, "init", "-b", "main")
    print(f"Created {destination}; independent Git repository, no remote, no initial commit.")
    print("Customize docs/PROJECT.md and agent-base.json, then run tools/setup.sh and tools/ci.sh quick --require-project.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    parser.add_argument("--name")
    args = parser.parse_args()
    try:
        create(args.destination, args.name if args.name is not None else Path(args.destination).name)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"[new-project] {exc}")
