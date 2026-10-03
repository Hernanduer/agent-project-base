"""Exercise Git mutations only in disposable repositories with isolated config."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class GitFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agent base test ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "base repo"
        (self.root / "tools").mkdir(parents=True)
        for name in ("common.py", "worktree.py", "wt.sh", "new_project.py"):
            shutil.copy2(ROOT / "tools" / name, self.root / "tools" / name)
        shutil.copy2(ROOT / "agent-base.json", self.root / "agent-base.json")
        (self.root / ".gitignore").write_text("build/\n__pycache__/\n*.local\n")
        (self.root / "tracked.txt").write_text("initial\n")
        (self.root / "docs").mkdir()
        (self.root / "docs/PROJECT.md").write_text("fixture\n")
        (self.root / "tools/ci.sh").write_text("#!/usr/bin/env bash\nset -euo pipefail\ntest ! -f fail-gate\n")
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_AUTHOR_NAME="Base Test", GIT_AUTHOR_EMAIL="base-test@example.invalid",
                        GIT_COMMITTER_NAME="Base Test", GIT_COMMITTER_EMAIL="base-test@example.invalid",
                        GIT_EDITOR="true", GIT_SEQUENCE_EDITOR="true")
        self.git("init", "-b", "main")
        self.commit("fixture")

    def command(self, argv, cwd=None, check=True):
        result = subprocess.run(argv, cwd=cwd or self.root, env=self.env, capture_output=True, text=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def git(self, *args, cwd=None, check=True):
        return self.command(["git", *args], cwd=cwd, check=check)

    def commit(self, message, cwd=None):
        self.git("add", ".", cwd=cwd)
        self.git("commit", "-m", message, cwd=cwd)

    def wt(self, *args, cwd=None, check=True):
        return self.command(["bash", "tools/wt.sh", *args], cwd=cwd, check=check)

    def task(self, name="feature"):
        self.wt("new", name)
        return self.root.parent / (self.root.name + "-wt") / name


class WorktreeTests(GitFixture):
    def test_create_list_sync_merge_remove(self):
        task = self.task()
        self.assertIn(str(task), self.wt("ls").stdout)
        (self.root / "main-only.txt").write_text("base advanced\n")
        self.commit("base advanced")
        (task / "feature.txt").write_text("feature\n")
        self.commit("feature", cwd=task)
        self.wt("sync", cwd=task)
        self.assertTrue((task / "main-only.txt").is_file())
        self.wt("merge", cwd=task)
        self.assertEqual((self.root / "feature.txt").read_text(), "feature\n")
        self.wt("rm", "feature")
        self.assertFalse(task.exists())
        self.assertNotEqual(self.git("show-ref", "--verify", "refs/heads/task/feature", check=False).returncode, 0)

    def test_failed_gate_leaves_main_unchanged(self):
        before = self.git("rev-parse", "HEAD").stdout
        task = self.task()
        (task / "fail-gate").write_text("fail\n")
        self.commit("failing change", cwd=task)
        result = self.wt("merge", "feature", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, before)
        self.assertTrue(task.exists())

    def test_dirty_and_untracked_task_refused(self):
        task = self.task()
        for path in (task / "tracked.txt", task / "new.txt"):
            previous = path.read_text() if path.exists() else None
            path.write_text("uncommitted\n")
            self.assertNotEqual(self.wt("merge", "feature", check=False).returncode, 0)
            self.assertNotEqual(self.wt("rm", "feature", check=False).returncode, 0)
            if previous is None:
                path.unlink()
            else:
                path.write_text(previous)

    def test_unmerged_task_not_removed(self):
        task = self.task()
        (task / "feature.txt").write_text("keep\n")
        self.commit("unmerged", cwd=task)
        self.assertNotEqual(self.wt("rm", "feature", check=False).returncode, 0)
        self.assertTrue((task / "feature.txt").is_file())

    def test_dirty_main_blocks_creation_and_merge(self):
        task = self.task()
        (self.root / "tracked.txt").write_text("user edit\n")
        self.assertNotEqual(self.wt("new", "other", check=False).returncode, 0)
        self.assertNotEqual(self.wt("merge", "feature", check=False).returncode, 0)
        self.assertEqual((self.root / "tracked.txt").read_text(), "user edit\n")

    def test_task_name_cannot_escape_and_limit_enforced(self):
        self.assertNotEqual(self.wt("new", "../escape", check=False).returncode, 0)
        self.task("one")
        self.task("two")
        self.task("three")
        self.assertNotEqual(self.wt("new", "four", check=False).returncode, 0)
        self.assertEqual(self.wt("new", "one").returncode, 0)

    def test_base_movement_during_gate_refused(self):
        task = self.task()
        # Reproduce an external writer that ignores the helper's merge lock.
        gate = ("#!/usr/bin/env bash\nset -euo pipefail\n"
                "git -C \"$TEST_BASE_CHECKOUT\" -c user.name=Test -c user.email=test@example.invalid "
                "commit --allow-empty -m external-move\n")
        (task / "tools/ci.sh").write_text(gate)
        (task / "feature.txt").write_text("must not land\n")
        self.commit("gate races with external commit", cwd=task)
        self.env["TEST_BASE_CHECKOUT"] = str(self.root)
        result = self.wt("merge", "feature", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("base branch moved", result.stderr)
        self.assertFalse((self.root / "feature.txt").exists())

    def test_gate_mutations_refused(self):
        task = self.task()
        (task / "tools/ci.sh").write_text("#!/usr/bin/env bash\necho surprise > tracked.txt\n")
        self.commit("gate edits a tracked file", cwd=task)
        before = self.git("rev-parse", "HEAD").stdout
        self.assertNotEqual(self.wt("merge", "feature", check=False).returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, before)

    def test_gate_switching_task_branch_is_refused(self):
        task = self.task()
        (task / "tools/ci.sh").write_text("#!/usr/bin/env bash\ngit checkout -b unexpected-branch\n")
        self.commit("gate switches branch", cwd=task)
        before = self.git("rev-parse", "HEAD").stdout
        self.assertNotEqual(self.wt("merge", "feature", check=False).returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, before)


class GeneratorTests(GitFixture):
    def generate(self, destination, check=True):
        return self.command([sys.executable, "tools/new_project.py", str(destination), "--name", "Fresh Project"], check=check)

    def test_independent_repository_and_tracked_files_only(self):
        (self.root / "private.local").write_text("must stay here\n")
        destination = self.root.parent / "fresh project"
        self.generate(destination)
        self.assertTrue((destination / ".git").is_dir())
        self.assertFalse((destination / "private.local").exists())
        self.assertEqual(self.git("remote", cwd=destination).stdout, "")
        self.assertNotEqual(self.git("rev-parse", "--verify", "HEAD", cwd=destination, check=False).returncode, 0)
        data = json.loads((destination / "agent-base.json").read_text())
        self.assertEqual(data["project"], "Fresh Project")
        self.assertEqual(data["checks"], {"quick": [], "full": []})
        self.assertIn("Fresh Project", (destination / "docs/PROJECT.md").read_text())

    def test_existing_destination_preserved(self):
        destination = self.root.parent / "existing"
        destination.mkdir()
        (destination / "valuable.txt").write_text("keep\n")
        self.assertNotEqual(self.generate(destination, check=False).returncode, 0)
        self.assertEqual((destination / "valuable.txt").read_text(), "keep\n")

    def test_dirty_source_and_nested_destination_refused(self):
        destination = self.root.parent / "fresh"
        (self.root / "untracked.txt").write_text("do not copy\n")
        self.assertNotEqual(self.generate(destination, check=False).returncode, 0)
        self.assertFalse(destination.exists())
        (self.root / "untracked.txt").unlink()
        self.assertNotEqual(self.generate(self.root / "nested", check=False).returncode, 0)
        self.assertFalse((self.root / "nested").exists())


if __name__ == "__main__":
    unittest.main()
