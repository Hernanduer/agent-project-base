"""Behavior checks for logging, hook protocols, and configured validation."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from common import config
from quiet import run


class QuietTests(unittest.TestCase):
    def test_failure_exit_status_full_log_and_bounded_console(self):
        with tempfile.TemporaryDirectory(prefix="quiet space ") as directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code, log = run([sys.executable, "-c", "print('x' * 2000 + '\\n' * 500); print('ERROR: deliberate'); raise SystemExit(23)"], Path(directory))
            self.assertEqual(code, 23)
            self.assertIn("ERROR: deliberate", Path(log).read_text())
            self.assertGreater(Path(log).stat().st_size, 2000)
            self.assertLess(len(output.getvalue()), 13000)

    def test_missing_command_returns_failure_and_log(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            code, log = run(["agent-base-command-that-does-not-exist"], Path(directory))
            self.assertEqual(code, 127)
            self.assertTrue(Path(log).is_file())

    def test_preserves_arguments_and_current_directory(self):
        with tempfile.TemporaryDirectory(prefix="argument space ") as directory:
            result = subprocess.run(["bash", str(ROOT / "tools/q.sh"), sys.executable, "-c",
                                     "import pathlib,sys; print(pathlib.Path.cwd()); print(sys.argv[1])",
                                     "literal $(not-a-command) and spaces"], cwd=directory, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(directory, result.stdout)
            self.assertIn("literal $(not-a-command) and spaces", result.stdout)
            self.assertFalse((Path(directory) / "build").exists())
            self.assertIn(str(ROOT / "build/logs"), result.stdout)


class HookTests(unittest.TestCase):
    def call(self, name, payload):
        result = subprocess.run([sys.executable, str(ROOT / "tools/hooks" / (name + ".py"))],
                                input=payload if isinstance(payload, str) else json.dumps(payload),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def test_large_code_read_denied_and_bounded_read_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "big file.py"
            path.write_text("pass\n" * 220)
            event = {"tool_name": "Read", "tool_input": {"file_path": str(path)}}
            reply = self.call("read_gate", event)
            self.assertEqual(reply["hookSpecificOutput"]["permissionDecision"], "deny")
            event["tool_input"]["limit"] = 220
            self.assertIsNone(self.call("read_gate", event))

    def test_quoted_relative_cat_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "big file.py").write_text("pass\n" * 220)
            event = {"cwd": directory, "tool_name": "Bash", "tool_input": {"command": "cat 'big file.py'"}}
            self.assertIsNotNone(self.call("read_gate", event))
            event["tool_input"]["command"] += " | head -20"
            self.assertIsNone(self.call("read_gate", event))

    def test_documents_and_small_code_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, size in [("large.md", 400), ("small.py", 10)]:
                path = Path(directory) / name
                path.write_text("line\n" * size)
                self.assertIsNone(self.call("read_gate", {"tool_name": "Read", "tool_input": {"file_path": str(path)}}))

    def test_malformed_payloads_fail_open(self):
        for hook in ("read_gate", "no_nested_agents"):
            for payload in ("not-json", "null", "[]", '{}'):
                with self.subTest(hook=hook, payload=payload):
                    self.assertIsNone(self.call(hook, payload))

    def test_nested_delegation_blocked_main_and_other_tools_allowed(self):
        for tool in ("Agent", "Task", "Workflow"):
            self.assertIsNotNone(self.call("no_nested_agents", {"tool_name": tool, "agent_id": "child"}))
            self.assertIsNone(self.call("no_nested_agents", {"tool_name": tool}))
        self.assertIsNone(self.call("no_nested_agents", {"tool_name": "Read", "agent_id": "child"}))
        self.assertIsNotNone(self.call("no_nested_agents", {"tool_name": "Agent", "transcript_path": r"C:\project\subagents\child.jsonl"}))


class ConfigurationTests(unittest.TestCase):
    def test_rejects_shell_string_and_invalid_limits(self):
        original = json.loads((ROOT / "agent-base.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            data = dict(original, checks={"quick": [{"name": "bad", "argv": "echo pass"}], "full": []})
            (path / "agent-base.json").write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                config(path)
            data = dict(original, max_worktrees=0)
            (path / "agent-base.json").write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                config(path)

    def test_require_project_refuses_empty_gate(self):
        import ci
        with mock.patch.object(ci, "config", return_value={"checks": {"quick": []}}), \
                mock.patch.object(sys, "argv", ["ci.py", "quick", "--require-project"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ci.main(), 2)

    def test_configured_failure_propagates_and_skips_later_steps(self):
        # The fixture has one trivial starter test, avoiding recursive execution
        # of this suite while testing the real CI runner end to end.
        with tempfile.TemporaryDirectory(prefix="ci fixture ") as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "tools", root / "tools", ignore=shutil.ignore_patterns("__pycache__"))
            (root / "tools/check.py").write_text("print('fixture structure')\n")
            (root / "tests/base").mkdir(parents=True)
            (root / "tests/base/test_smoke.py").write_text("import unittest\nclass Smoke(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n")
            data = json.loads((ROOT / "agent-base.json").read_text())
            data["checks"]["quick"] = [
                {"name": "deliberate failure", "argv": [sys.executable, "-c", "print('FAIL expected'); raise SystemExit(7)"]},
                {"name": "must not run", "argv": [sys.executable, "-c", "open('unexpected', 'w').close()"]},
            ]
            (root / "agent-base.json").write_text(json.dumps(data))
            result = subprocess.run(["bash", "tools/ci.sh", "quick", "--require-project"], cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
            self.assertFalse((root / "unexpected").exists())
            report = json.loads(next((root / "build/ci").glob("*.json")).read_text())
            self.assertEqual(report["exit_code"], 7)
            self.assertTrue(report["application_checks_configured"])
            self.assertEqual(len(report["steps"]), 3)


if __name__ == "__main__":
    unittest.main()
