#!/bin/sh
set -eu
task_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then
    exec "$PYTHON" -B "$task_dir/replay.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 -B "$task_dir/replay.py" "$@"
else
    exec python -B "$task_dir/replay.py" "$@"
fi
