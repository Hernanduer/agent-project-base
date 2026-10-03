#!/usr/bin/env bash
# Read-only diagnostics; no package installs or global configuration changes.
set -euo pipefail
exec python3 "$(dirname "$0")/doctor.py" "$@"
