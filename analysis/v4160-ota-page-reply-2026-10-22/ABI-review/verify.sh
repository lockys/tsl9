#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then
    exec "$PYTHON" -B "$HERE/verify.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 -B "$HERE/verify.py" "$@"
else
    exec python -B "$HERE/verify.py" "$@"
fi
