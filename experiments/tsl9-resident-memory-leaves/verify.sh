#!/bin/sh
set -eu
TASK_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
exec "${PYTHON:-python3}" -B "$TASK_DIR/verify_host.py" "$@"
