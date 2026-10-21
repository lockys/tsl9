#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then
    exec "$PYTHON" -B "$script_dir/verify.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 -B "$script_dir/verify.py" "$@"
else
    exec python -B "$script_dir/verify.py" "$@"
fi
