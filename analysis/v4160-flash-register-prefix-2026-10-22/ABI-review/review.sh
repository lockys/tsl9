#!/bin/sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-python3}
export PYTHONUTF8=1
exec "$PYTHON" -B "$SCRIPT_DIR/review.py" "$@"
