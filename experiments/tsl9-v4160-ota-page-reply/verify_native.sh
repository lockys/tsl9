#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
if [ -n "${PYTHON:-}" ]; then PY=$PYTHON
elif command -v python3 >/dev/null 2>&1; then PY=python3
else PY=python
fi
exec "$PY" -B "$ROOT/experiments/tsl9-v4160-ota-page-reply/verify_native.py" --project-root "$ROOT" "$@"
