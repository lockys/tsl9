#!/bin/sh
set -eu
if [ -n "${PYTHON:-}" ]; then exec "$PYTHON" -B "$(dirname "$0")/verify.py" "$@"; fi
if command -v python3 >/dev/null 2>&1; then exec python3 -B "$(dirname "$0")/verify.py" "$@"; fi
exec python -B "$(dirname "$0")/verify.py" "$@"
