#!/bin/sh
set -eu
entry_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python_cmd=${PYTHON:-python3}
if ! command -v "$python_cmd" >/dev/null 2>&1; then python_cmd=python; fi
exec "$python_cmd" "$entry_dir/verify-v2.py" "$@"
