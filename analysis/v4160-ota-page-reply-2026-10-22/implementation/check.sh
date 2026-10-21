#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
if [ -n "${PYTHON:-}" ]; then PY=$PYTHON
elif command -v python3 >/dev/null 2>&1; then PY=python3
else PY=python
fi
exec "$PY" -B "$(dirname -- "$0")/check.py" --project-root "$ROOT" "$@"
