#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then
    exec "$PYTHON" -B "$HERE/native.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 -B "$HERE/native.py" "$@"
else
    exec python -B "$HERE/native.py" "$@"
fi
