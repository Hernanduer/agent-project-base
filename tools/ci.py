"""Run starter checks and explicitly configured application checks."""
import argparse
import datetime
import json
import sys
import tempfile
from pathlib import Path

from common import ROOT, config
from quiet import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lane", nargs="?", choices=("quick", "full"), default="quick")
    parser.add_argument("--require-project", action="store_true",
                        help="fail unless application quick checks are configured")
    args = parser.parse_args()
    data = config()
    if not data["checks"]["quick"]:
        print("[ci] STARTER ONLY: application quick checks are not configured", flush=True)
        if args.require_project:
            return 2
    steps = [
        {"name": "starter structure", "argv": [sys.executable, "tools/check.py"]},
        {"name": "starter behavior", "argv": [sys.executable, "-m", "unittest", "discover", "-s", "tests/base", "-v"]},
        *data["checks"]["quick"],
        *(data["checks"]["full"] if args.lane == "full" else []),
    ]
    report = {"project": data["project"], "lane": args.lane,
              "application_checks_configured": bool(data["checks"]["quick"]), "steps": []}
    code = 0
    for step in steps:
        print(f"[ci] {step['name']}", flush=True)
        code, log = run(step["argv"])
        report["steps"].append({"name": step["name"], "exit_code": code,
                                "log": str(Path(log).relative_to(ROOT))})
        if code:
            break
    report["exit_code"] = code
    report["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    directory = ROOT / "build" / "ci"
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", prefix="summary-", suffix=".json", dir=directory, delete=False) as f:
        json.dump(report, f, indent=2)
        print(f"[ci] {'PASS' if code == 0 else 'FAIL'} summary={f.name}")
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        sys.exit(f"[ci] {exc}")
