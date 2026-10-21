#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then
    exec "$PYTHON" "$script_dir/check-review.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 "$script_dir/check-review.py" "$@"
else
    exec python "$script_dir/check-review.py" "$@"
fi
