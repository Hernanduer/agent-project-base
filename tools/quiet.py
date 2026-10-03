"""Run a command with bounded console output and a complete, unique log."""
import collections
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from common import ROOT


def run(argv, cwd=ROOT, log_root=None):
    directory = Path(log_root or cwd) / "build" / "logs"
    directory.mkdir(parents=True, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix="run-", suffix=".log", dir=directory)
    try:
        with os.fdopen(fd, "w") as log:
            try:
                result = subprocess.run(argv, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
                code = result.returncode if result.returncode >= 0 else 128 - result.returncode
            except OSError as exc:
                log.write(str(exc) + "\n")
                code = 127
        tail = collections.deque(maxlen=8)
        failures = []
        count = 0
        with open(path, errors="replace") as log:
            for line in log:
                count += 1
                tail.append(line[:1000].rstrip())
                if code and len(failures) < 12 and any(x in line.lower() for x in ("error", "fail", "traceback", "panicked")):
                    failures.append(line[:1000].rstrip())
        print(f"[q] exit={code} lines={count} log={path}", flush=True)
        for line in failures + list(tail):
            print(line)
        return code, path
    except KeyboardInterrupt:
        print(f"[q] interrupted; partial log={path}", file=sys.stderr)
        return 130, path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: tools/q.sh COMMAND [ARG ...]")
    # Preserve the caller's directory for commands such as package-local tests.
    sys.exit(run(sys.argv[1:], Path.cwd(), log_root=ROOT)[0])
