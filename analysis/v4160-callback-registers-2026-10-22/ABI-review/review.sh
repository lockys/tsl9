#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
if [ "${PYTHON:-}" ]; then
    runtime=$PYTHON
elif command -v python3 >/dev/null 2>&1; then
    runtime=python3
else
    runtime=python
fi
if [ "$#" -eq 0 ]; then
    exec "$runtime" -B "$script_dir/check.py"
fi
exec "$runtime" -B "$script_dir/review-ordered.py" "$@"
