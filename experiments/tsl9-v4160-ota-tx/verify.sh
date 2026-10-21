#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then py=$PYTHON
elif command -v python3 >/dev/null 2>&1; then py=python3
else py=python
fi
exec "$py" -X utf8 -B "$script_dir/verify_host.py" "$@"
