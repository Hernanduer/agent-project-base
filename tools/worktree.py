"""Isolated task branches and serialized, validated local fast-forward merges."""
import argparse
import contextlib
import re
import subprocess
import sys
import time
from pathlib import Path

from common import ROOT, clean, config, git


def worktrees():
    records = []
    for block in git(ROOT, "worktree", "list", "--porcelain").stdout.strip().split("\n\n"):
        record = {}
        for line in block.splitlines():
            key, _, value = line.partition(" ")
            record[key] = value
        records.append(record)
    return records


def require_clean(path):
    if not clean(path):
        raise ValueError(f"commit or move your changes first: {path}")
    for name in ("rebase-merge", "rebase-apply", "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD"):
        p = git(path, "rev-parse", "--path-format=absolute", "--git-path", name).stdout.strip()
        if Path(p).exists():
            raise ValueError(f"finish or abort the in-progress Git operation in {path}")


@contextlib.contextmanager
def merge_lock():
    try:
        import fcntl
    except ImportError:
        raise ValueError("local serialized merges require POSIX flock; use WSL or your PR workflow")
    common = Path(git(ROOT, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    with (common / "agent-base.merge.lock").open("a") as lock:
        deadline = time.monotonic() + 60
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise ValueError("another merge holds the lock; retry after it finishes")
                time.sleep(0.2)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("new", "ls", "sync", "merge", "rm"))
    parser.add_argument("task", nargs="?")
    args = parser.parse_args()
    data = config()
    base = data["base_branch"]
    trees = worktrees()
    if args.command == "ls":
        for tree in trees:
            print(f"{tree.get('branch', 'detached')} {tree['worktree']}")
        return 0
    task = args.task
    if not task:
        branch = git(ROOT, "symbolic-ref", "--short", "HEAD", check=False).stdout.strip()
        if branch.startswith("task/"):
            task = branch[5:]
    if not task or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", task):
        raise ValueError("provide a task name using lowercase letters, digits, dots, underscores, or hyphens")
    branch = "task/" + task
    main_tree = next((t for t in trees if t.get("branch") == "refs/heads/" + base), None)
    if main_tree is None:
        raise ValueError(f"the base branch {base!r} must be checked out in its own worktree")
    main_path = Path(main_tree["worktree"])
    target = next((t for t in trees if t.get("branch") == "refs/heads/" + branch), None)
    if args.command == "new":
        if target:
            print(target["worktree"])
            return 0
        require_clean(main_path)
        if sum(t.get("branch", "").startswith("refs/heads/task/") for t in trees) >= data["max_worktrees"]:
            raise ValueError("max_worktrees reached; finish and remove a task first")
        path = main_path.parent / (main_path.name + "-wt") / task
        path.parent.mkdir(parents=True, exist_ok=True)
        print(git(main_path, "worktree", "add", "-b", branch, str(path), base).stderr.strip())
        print(path)
        return 0
    if not target:
        raise ValueError(f"no worktree on {branch}; check 'git worktree list' for an interrupted rebase")
    path = Path(target["worktree"])
    require_clean(path)
    if args.command == "sync":
        print(git(path, "rebase", base).stdout.strip())
    elif args.command == "rm":
        if git(main_path, "merge-base", "--is-ancestor", branch, base, check=False).returncode:
            raise ValueError(f"{branch} has unmerged commits; worktree kept")
        git(main_path, "worktree", "remove", str(path))
        print(git(main_path, "branch", "-d", branch).stdout.strip())
    elif args.command == "merge":
        with merge_lock():
            require_clean(main_path)
            git(path, "rebase", base)
            base_tip = git(main_path, "rev-parse", "HEAD").stdout.strip()
            tested_tip = git(path, "rev-parse", "HEAD").stdout.strip()
            print(f"[wt] validating {tested_tip}", flush=True)
            gate = subprocess.run(["bash", "tools/ci.sh", "quick"], cwd=path)
            if gate.returncode:
                raise ValueError("validation failed; base branch was not moved by this helper")
            require_clean(path)
            require_clean(main_path)
            if git(main_path, "symbolic-ref", "--short", "HEAD").stdout.strip() != base:
                raise ValueError("base checkout switched branches during validation; retry")
            if git(main_path, "rev-parse", "HEAD").stdout.strip() != base_tip:
                raise ValueError("base branch moved during validation; retry to rebase and revalidate")
            if git(path, "rev-parse", "HEAD").stdout.strip() != tested_tip:
                raise ValueError("task branch moved during validation; retry")
            if (git(path, "symbolic-ref", "--short", "HEAD", check=False).stdout.strip() != branch
                    or git(main_path, "rev-parse", branch).stdout.strip() != tested_tip):
                raise ValueError("task checkout switched branches during validation; retry")
            print(git(main_path, "merge", "--ff-only", "--no-edit", branch).stdout.strip())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        sys.exit(f"[wt] {detail}")
