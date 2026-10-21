#!/bin/sh
set -eu
review_root=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then
    exec "$PYTHON" "$review_root/run-review.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 "$review_root/run-review.py" "$@"
else
    exec python "$review_root/run-review.py" "$@"
fi
