#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then
    exec "$PYTHON" -X utf8 -B "$script_dir/scan.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 -X utf8 -B "$script_dir/scan.py" "$@"
else
    exec python -X utf8 -B "$script_dir/scan.py" "$@"
fi
